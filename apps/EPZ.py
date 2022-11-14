import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
import folium
from typing import List
from folium.plugins import Draw


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


def app():
    st.title("Energy Plan Zero")
    st.header("Velg studieområde")
    lat = st.number_input('Lengdegrad', value = 60.3925)
    long = st.number_input('Breddegrad', value = 5.3233)
    scenario = st.radio('Velg scenario', options=['1', '2', '3', '4', '5'], horizontal=True)
    st.header("Scenariobygger")
    st.subheader("1) Plasser ut bygg")
    st.write("Bruk knappene til venstre")
    m = leafmap.Map(locate_control=True, center=[lat, long], zoom=17, Draw_export = True)
    m.add_basemap("ROADMAP")
    output = st_folium(m, key="init", width=1000, height=600)

    st.subheader("2) Gi byggene attributter")
    for i in range(0, len(output["all_drawings"])):
        st.write(f"Bygg {i}")
        output["all_drawings"][i]["properties"]["id"] = i
        output["all_drawings"][i]["properties"]["area"] = st.number_input("Bruttoareal (BRA)", value=150, step=10, key=f"area_{i}")
        output["all_drawings"][i]["properties"]["standard"] = st.selectbox("Velg energistandard", options=["Nytt", "Gammelt"], key=f"standard_{i}")
        st.write(output["all_drawings"][i])
    
    st.header("Energibehov")

    #m = show_map(center=[lat,long], zoom=17)
    #output = st_folium(m, key="init", width=1000, height=600)
    #st.write(output)





