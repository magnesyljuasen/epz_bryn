import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
import folium
from typing import List
from folium.plugins import Draw
import pandas as pd
import numpy as np
import io
#import geopandas
from src.scripts import input, adjust, temperature, demand, geology, geoenergy, environment, costs

def download_array(arr, name):
    # Create an in-memory buffer
    with io.BytesIO() as buffer:
        # Write array to buffer
        np.savetxt(buffer, arr, delimiter=",")
        st.download_button(
            label="Last ned timeserie",
            data = buffer, # Download buffer
            file_name = f'{name}.csv',
            mime='text/csv'
        ) 


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
            "polygon": True,
            "marker": False,
            "circlemarker": False,
            "rectangle": False,
        },
    ).add_to(m)
    return m

def app(lat, long):
    st.subheader("*1) Plasser ut bygg*")
    st.write("Bruk knappene til venstre i kartet")
    #m = leafmap.Map(locate_control=True, center=[lat, long], zoom=17)
    #m.add_basemap("ROADMAP")
    m = show_map(center=[lat, long], zoom=17)

    #counties_gdf = geopandas.read_file('https://storage.googleapis.com/co-publicdata/lm_cnty.zip')
    #folium.GeoJson(data=counties_gdf["geometry"]).add_to(m)

    st.caption("Mulighet til å legge inn mange flere lag")
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

    
    if output["all_drawings"] != None:
        with st.sidebar:
            st.subheader("*2) Gi byggene attributter*")
            st.caption("TO DO: Kan gjøres mer brukervennlig med last_clicked og shape_area som placeholder_verdi på bygg. Aktiv st_expander kan holdes åpen, resten lukket.")
            for i in range(0, len(output["all_drawings"])):
                with st.expander(f"Bygg {i+1}"):
                    path = output["all_drawings"][i]["properties"]
                    path["name"] = st.text_input("Navn", value=f"Bygg {i+1}")
                    path["area"] = st.number_input("BRA", value=150, step=10, key=f"area_{i}")
                    path["scenario"] = st.selectbox("Scenario", options=["1", "2", "3", "4", "5"], key=f"scenario_{i}")
                    #path["standard"] = st.selectbox("Energistandard", options=["Nytt", "Gammelt"], key=f"standard_{i}")
                    #path["category"] = st.selectbox("Kategori", options=["Hus", "Skole", "Barnehage"], key=f"category_{i}")
                    path["standard"] = 0
                    path["category"] = 0
                    st.markdown("---")

        with st.sidebar:
            st.markdown("---")
            with st.expander("Se bygningstabell"):
                st.caption("TO DO: tabell -> spatial dataframe")
                i_list = []
                name_list = []
                area_list = []
                standard_list = []
                category_list = []
                scenario_list = []
                for i in range(0, len(output["all_drawings"])):
                    # for hvert bygg
                    path = output["all_drawings"][i]["properties"]
                    i_list.append(i)
                    name_list.append(path["name"])
                    area_list.append(path["area"])
                    standard_list.append(path["standard"])
                    category_list.append(path["category"])
                    scenario_list.append(path["scenario"])
                
                df = pd.DataFrame(data={'ID' : i_list, 'Navn' : name_list, 'Areal' : area_list, 'Standard' : standard_list, 'Kategori' : category_list, 'Scenario' : scenario_list})

                st.write(df)

        if st.checkbox("Beregn energibehov"):
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5"])
            with tab1:
                st.header("*2) Energibehov*")
                st.write("Verktøyet beregner nå energibehov for alle byggene")

                # hente inn temperatur
                temperature_obj = temperature.Temperature()
                temperature_obj.closest_station(lat, long)
                temperature_obj.process(temperature_obj.id)

                space_heating_arr_sum = 0
                dhw_arr_sum = 0
                for i in range(0, len(df)):
                    # beregne energibehov
                    demand_obj = demand.Demand()
                    demand_obj.from_file(area_list[i], temperature_obj.id)
                    demand_obj.update()
                    
                    with st.expander(f"{name_list[i]}"):
                        st.write(f"**Romoppvarming**, {int(np.sum(demand_obj.space_heating_arr))} kWh")
                        st.line_chart(demand_obj.space_heating_arr)

                        st.write(f"**Tappevann**, {int(np.sum(demand_obj.dhw_arr))} kWh")
                        st.line_chart(demand_obj.dhw_arr)

                        st.write(f"**Termisk behov**, {int(np.sum(demand_obj.space_heating_arr + demand_obj.dhw_arr).flatten())} kWh")
                        thermal_arr = (demand_obj.space_heating_arr + demand_obj.dhw_arr).flatten()
                        st.line_chart(thermal_arr)

                        st.write(f"**Termisk behov, varighetskurve**")
                        st.line_chart(np.sort(thermal_arr.flatten())[::-1])

                        st.write("**Verdier**")
                        st.write(f"Maks effekt {int(max(thermal_arr))} kW")

                        download_array(thermal_arr, f"termisk_energibehov_{name_list[i]}")

                    space_heating_arr_sum += demand_obj.space_heating_arr
                    dhw_arr_sum += demand_obj.dhw_arr


                st.markdown("---")
                with st.expander("Samlet energibehov for alle bygg", expanded=True):
                    st.write(f"**Romoppvarming**, {int(np.sum(space_heating_arr_sum))} kWh")
                    st.line_chart(space_heating_arr_sum)

                    st.write(f"**Tappevann**, {int(np.sum(dhw_arr_sum))} kWh")
                    st.line_chart(dhw_arr_sum)

                    st.write(f"**Termisk behov**, {int(np.sum(space_heating_arr_sum + dhw_arr_sum).flatten())} kWh")
                    thermal_arr = (space_heating_arr_sum + dhw_arr_sum).flatten()
                    st.line_chart(thermal_arr)

                    st.write(f"**Termisk behov, varighetskurve**")
                    st.line_chart(np.sort(thermal_arr.flatten())[::-1])

                    st.write("**Verdier**")
                    st.write(f"Maks effekt {int(max(thermal_arr))} kW")

                    download_array(thermal_arr, f"termisk_energibehov_alle_bygg")

                #st.markdown("---")
                #st.header("*3) Grunnvarmepotensial*")

                #adjust_obj = adjust.Adjust(1.5, int(np.sum(space_heating_arr_sum)), int(np.sum(dhw_arr_sum)), 10, 5, 3.0, dhw_arr_sum, space_heating_arr_sum)
                #if adjust_obj.start == True:
                #    geoenergy_obj = geoenergy.Geoenergy((adjust_obj.dhw_arr + adjust_obj.space_heating_arr), 
                #        temperature_obj.average_temperature, adjust_obj.cop, adjust_obj.thermal_conductivity, 
                #        adjust_obj.groundwater_table, adjust_obj.energycoverage)

                #st.header("*4) Solenergipotensial*")
                #st.write("...")

                #st.header("*5) Sammenstilt behov og produksjon")








