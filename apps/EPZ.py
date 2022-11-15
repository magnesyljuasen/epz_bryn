import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
import folium
from typing import List
from folium.plugins import Draw
import pandas as pd


def show_map(center: List[float], zoom: int) -> folium.Map:
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        control_scale=True,
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',  # noqa: E501
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
            "rectangle": True,
        },
    ).add_to(m)
    return m


def app(lat, long):
    st.header("Scenariobygger")
    st.subheader("*1) Plasser ut bygg*")
    st.write("Bruk knappene til venstre i kartet")
    m = leafmap.Map(locate_control=True, center=[lat, long], zoom=17)
    m.add_basemap("ROADMAP")
    output = st_folium(m, key="init", width=1000, height=600)

    
    if output["all_drawings"] != None:
        with st.sidebar:
            st.subheader("*2) Gi byggene attributter*")
            st.caption("TO DO: Kan gjøres mer brukervennlig med last_clicked")
            for i in range(0, len(output["all_drawings"])):
                with st.expander(f"Bygg {i+1}"):
                    path = output["all_drawings"][i]["properties"]
                    path["name"] = st.text_input("Navn", value=f"Bygg {i+1}")
                    path["area"] = st.number_input("BRA", value=150, step=10, key=f"area_{i}")
                    path["standard"] = st.selectbox("Energistandard", options=["Nytt", "Gammelt"], key=f"standard_{i}")
                    path["category"] = st.selectbox("Kategori", options=["Hus", "Skole", "Barnehage"], key=f"category_{i}")
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
                for i in range(0, len(output["all_drawings"])):
                    # for hvert bygg
                    path = output["all_drawings"][i]["properties"]
                    i_list.append(i)
                    name_list.append(path["name"])
                    area_list.append(path["area"])
                    standard_list.append(path["standard"])
                    category_list.append(path["category"])
                
                df = pd.DataFrame(data={'ID' : i_list, 'Navn' : name_list, 'Areal' : area_list, 'Standard' : standard_list, 'Kategori' : category_list})

                st.write(df)

    if st.checkbox("Gå videre"):
        st.header("*2) Energibehov*")
        st.write("Verktøyet beregner nå energibehov for alle byggene")






