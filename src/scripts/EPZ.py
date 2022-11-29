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
from src.scripts import input, adjust, temperature, demand, geology, geoenergy, environment, costs
from energibehov import Energibehov

def visualize_demands(space_heating_arr, dhw_arr, df, i, name):
    st.write(f"**Romoppvarming**, {int(np.sum(space_heating_arr))} kWh")
    st.line_chart(space_heating_arr)

    st.write(f"**Tappevann**, {int(np.sum(dhw_arr))} kWh")
    st.line_chart(dhw_arr)

    st.write(f"**Termisk behov**, {int(np.sum(space_heating_arr + dhw_arr).flatten())} kWh")
    thermal = (space_heating_arr + dhw_arr).flatten()
    st.line_chart(thermal)

    st.write(f"**Termisk behov, varighetskurve**")
    st.line_chart(np.sort(thermal.flatten())[::-1])

    st.write("**Verdier**")
    st.write(f"Maks effekt {int(max(thermal))} kW")

    download_array(thermal, f"{name}_{df['ID'][i]}")

def download_array(arr, name):
    # Create an in-memory buffer
    with io.BytesIO() as buffer:
        # Write array to buffer
        np.savetxt(buffer, arr, delimiter=",")
        st.download_button(
            label="Last ned timeserie",
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
    return {"color":"blue", "weight":2}

def app(lat, long):
    st.header("*1) Bygningsmasse fra modell*")
    
    #-- Kart --
    m = show_map(center=[lat, long], zoom=16)
    
    buildings_gdf = geopandas.read_file('src/data/sluppen.zip')
    buildings_df = buildings_gdf[['ID', 'BRA', 'Kategori', 'Standard']]
    folium.GeoJson(data=buildings_gdf["geometry"]).add_to(m)

    uc = '\u00B2'
    feature = folium.features.GeoJson(buildings_gdf,
    name='ID',
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields= ["ID", "BRA"],aliases=["ID: ", f"BRA (m{uc}): "],labels=True))
    m.add_child(feature)

    #-- Energibehov fra tabell --

    energy_efficiency = st.selectbox("Velg energistandard for alle bygg", options=["Gammelt", "Energieffektiv (TEK10/TEK17)", "Passivhus"], index=1)
    if energy_efficiency == "Gammelt":
        buildings_df['Standard'][0:len(buildings_df)] = "X"
    if energy_efficiency == "Energieffektiv (TEK10/TEK17)":
        buildings_df['Standard'][0:len(buildings_df)] = "Y"
    if energy_efficiency == "Passivhus":
        buildings_df['Standard'][0:len(buildings_df)] = "Z"
    
    #with st.expander("Se bygningstabell"):
    #    st.write(buildings_df)

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

    df = pd.DataFrame(data={'ID' : buildings_df['ID'], 'Areal' : buildings_df['BRA'], 'Standard' : buildings_df['Standard'], 'Kategori' : buildings_df['Kategori']})
    
    st.header("*2) Energibehov*")
    if st.checkbox("Beregn energibehov"):
        #tab1, tab2, tab3 = st.tabs(["Scenario 1", "Scenario 2", "Scenario 3"])
        #with tab1:
        with st.sidebar:
            st.header("Energibehov per bygg")
            st.write("Verktøyet beregner nå termisk og elektrisk energibehov per bygg")
        space_heating_arr_sum = 0
        dhw_arr_sum = 0
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
                    visualize_demands(space_heating_arr, dhw_arr, df, i, "termisk_energibehov")

            space_heating_arr_sum += space_heating_arr
            dhw_arr_sum += dhw_arr

        st.markdown("---")
        with st.expander("Samlet energibehov for alle bygg", expanded=True):
            visualize_demands(space_heating_arr, dhw_arr, df, i, "termisk_energibehov_alle")

        










