import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
import folium
from typing import List
from folium.plugins import Draw
import pandas as pd
import numpy as np
import io
import geopandas
import altair as alt
from PIL import Image
from src.scripts import input, adjust, temperature, demand, geology, geoenergy, environment, costs
from energibehov import Energibehov

def plot(y, name):
    if name == "Electric":
        plot_color = "#FFC358"
    elif name == 'Space_heating':
        plot_color = "#1d3c34"
    elif name == 'DHW':
        plot_color = "#428977"
    else:
        plot_color = '#1d3c34'

    x = np.arange(8760)
    source = pd.DataFrame({
    'x': x,
    'y': y})

    c = alt.Chart(source).mark_bar(size=0.75).encode(
        x=alt.X('x', scale=alt.Scale(domain=[0,8760]), title="Timer i ett år"),
        y=alt.Y('y', title="kW"),
        color = alt.value(plot_color))
    st.altair_chart(c, use_container_width=True)

def visualize_demands(space_heating_arr, dhw_arr, electric_arr, df, i, name):
    st.write(f"**Elektrisk behov**, {int(np.sum(electric_arr)):,} kWh".replace(',', ' '))
    plot(electric_arr, "Electric")
    
    st.write(f"**Romoppvarming**, {int(np.sum(space_heating_arr)):,} kWh".replace(',', ' '))
    plot(space_heating_arr, "Space_heating")

    st.write(f"**Tappevann**, {int(np.sum(dhw_arr)):,} kWh".replace(',', ' '))
    plot(dhw_arr, "DHW")

    st.write(f"**Sammenstilt termisk behov (romoppvarming + tappevann)**, {int(np.sum(space_heating_arr + dhw_arr).flatten()):,} kWh".replace(',', ' '))
    thermal_arr = (space_heating_arr + dhw_arr).flatten()
    plot(thermal_arr, "Thermal")

    st.write(f"**Termisk behov, varighetskurve**")
    plot(np.sort(thermal_arr.flatten())[::-1], 'Thermal')

    st.write("**Verdier**")
    st.write(f"Termisk: Maks effekt {int(max(thermal_arr))} kW")
    st.write(f"Elektrisk: Maks effekt {int(max(electric_arr))} kW")

    download_array(thermal_arr, f"{name}_{df['ID'][i]}", "Termisk")
    download_array(electric_arr, f"{name}_{df['ID'][i]}", "Elektrisk")

def download_array(arr, name, info):
    # Create an in-memory buffer
    with io.BytesIO() as buffer:
        # Write array to buffer
        np.savetxt(buffer, arr, delimiter=",", fmt='%i')
        st.download_button(
            label=f"Last ned timeserie, {info}",
            data = buffer, # Download buffer
            file_name = f'{name}.csv',
            mime='text/csv') 

def show_map(center: List[float], zoom: int) -> folium.Map:
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        control_scale=True,
        tiles="openstreetmap",
    )
    Draw(
        export=False,
        position="topleft",
        draw_options={
            "polyline": False,
            "poly": False,
            "circle": False,
            "polygon": False,
            "marker": False,
            "circlemarker": False,
            "rectangle": False,
        },
    ).add_to(m)
    return m

def style_function(x):
    return {"color":"black", "weight":2}

def app(lat, long):
    st.header("*1) Modell*")
    with st.expander("Se 3D modell"):
        uc = '\u00B2'
        
        image = Image.open('src\data\Arealer.png')

        st.image(image, caption=f'Bygninger og bruttoareal (m{uc}) fra modell')
    
    #-- Kart --
    m = show_map(center=[lat, long], zoom=16)
    
    buildings_gdf = geopandas.read_file('src/data/sluppen.zip')
    buildings_df = buildings_gdf[['ID', 'BRA', 'Kategori', 'Standard']]
    #folium.GeoJson(data=buildings_gdf["geometry"]).add_to(m)

    feature = folium.features.GeoJson(buildings_gdf,
    name='Bygningsmasse',
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields= ["ID", "BRA"],aliases=["ID: ", f"BTA (m{uc}): "],labels=True))
    m.add_child(feature)

    #-- Energibehov fra tabell --

    energy_efficiency = st.selectbox("Velg energistandard for alle bygg", options=["Gammelt", "Energieffektiv (TEK10/TEK17)", "Passivhus"], index=1)
    if energy_efficiency == "Gammelt":
        buildings_df['Standard'][0:len(buildings_df)] = "X"
    if energy_efficiency == "Energieffektiv (TEK10/TEK17)":
        buildings_df['Standard'][0:len(buildings_df)] = "Y"
    if energy_efficiency == "Passivhus":
        buildings_df['Standard'][0:len(buildings_df)] = "Z"
    
    
    df = pd.DataFrame(data={'ID' : buildings_df['ID'], 'Areal' : buildings_df['BRA'], 'Standard' : buildings_df['Standard'], 'Kategori' : buildings_df['Kategori']})
    
    selected_url = 'https://geo.ngu.no/mapserver/LosmasserWMS?request=GetCapabilities&service=WMS'
    selected_layer = 'Losmasse_flate'

    folium.raster_layers.WmsTileLayer(url = selected_url,
        layers = selected_layer,
        transparent = True, 
        control = True,
        fmt="image/png",
        name = 'Løsmasser',
        overlay = True,
        show = False,
        CRS = 'EPSG:900913',
        version = '1.3.0',
        ).add_to(m)

    folium.LayerControl().add_to(m)
    output = st_folium(m, width=700, height=600)

    # -- Beregne energibehov --
    st.info("Her kan du starte energiberegning for bygningsmassen.")
    if st.checkbox("Start beregning"):
        st.header("*2) Energibehov*")
        #tab1, tab2, tab3 = st.tabs(["Scenario 1", "Scenario 2", "Scenario 3"])
        #with tab1:
        with st.sidebar:
            st.header("Energibehov per bygg")
            st.write("Vi beregner nå termisk og elektrisk energibehov per bygg. Trykk på boksene under for å se behovene.")
        space_heating_arr_sum = 0
        dhw_arr_sum = 0
        electric_arr_sum = 0
        for i in range(0, len(df)):
            area = df['Areal'][i]
            standard = df['Standard'][i]
            category = df['Kategori'][i]

            building = Energibehov()
            electric_arr = building.hent_profil(category, standard, '1', area)
            dhw_arr = building.hent_profil(category, standard, '2', area)                
            space_heating_arr = building.hent_profil(category, standard, '3', area)

            with st.sidebar:
                with st.expander(f"Bygning ID: {df['ID'][i]}"):
                    visualize_demands(space_heating_arr, dhw_arr, electric_arr, df, i, "energibehov")

            space_heating_arr_sum += space_heating_arr
            dhw_arr_sum += dhw_arr
            electric_arr_sum += electric_arr

        st.markdown("---")
        with st.expander("Samlet energibehov for alle bygg", expanded=True):
            visualize_demands(space_heating_arr_sum, dhw_arr_sum, electric_arr_sum, df, i, "energibehov_alle")
        
        st.header("*3) Grunnvarme*")
        if st.checkbox ("Beregn antall energibrønner for å dekke 90 % av det termiske energibehovet"):
            geoenergy_obj = geoenergy.Geoenergy((space_heating_arr_sum + dhw_arr_sum), 8.5, 3.5, 3.0, 5, 90)
            
            st.write(f"Levert energi fra brønner: {geoenergy_obj.energy_gshp_delivered_sum:,} kWh".replace(',', ' '))
            st.write(f"Strøm til varmepumpe: {geoenergy_obj.energy_gshp_compressor_sum:,} kWh".replace(',', ' '))
            st.write(f"Spisslast (dekkes ikke av grunnvarme): {geoenergy_obj.energy_gshp_peak_sum:,} kWh".replace(',', ' '))

            number_of_wells = int(geoenergy_obj.energy_gshp_delivered_sum / 75 / 300)
            st.write(f"""Det trengs ca. {number_of_wells} brønner 
            med 300 meters dybde og 15 m mellomrom for å dekke 90 % av det termiske energibehovet til alle bygningene. 
            De resterende 10 % kalles spisslast og klarer ikke dekkes av energibrønner. 
            
            Energibrønner kan redusere termisk effekt med {int(max(geoenergy_obj.energy_arr) - geoenergy_obj.heat_pump_size)} kW. """)

            st.header("*4) Solenergi*")
            st.caption("Kommer...")


        










