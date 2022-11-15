 """
 c1, c2 = st.columns(2)
    with c1:
        output["last_active_drawing"]["properties"]["id"] = st.text_input("ID", key="id")
        output["last_active_drawing"]["properties"]["area"] = st.number_input("Bruttoareal (BRA)", value=150, step=10, key=f"area")
    with c2:
        output["last_active_drawing"]["properties"]["standard"] = st.selectbox("Velg energistandard", options=["Nytt", "Gammelt"], key=f"standard")
        output["last_active_drawing"]["properties"]["category"] = st.selectbox("Velg kategori", options=["Hus", "Skole", "Barnehage"], key=f"category")
    st.write(output["last_active_drawing"])
    #output["last_active_drawing"]["type"]["properties"]["area"] = st.number_input("Bruttoareal (BRA)", value=150, step=10, key=f"area")
"""


import streamlit as st
import time
from src.scripts import input, adjust, temperature, demand, geology, geoenergy, environment, costs

st.set_page_config(
    page_title="Bergvarmekalkulatoren",
    layout="centered")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

# adresse og boligareal
input_obj = input.Input()

# hente inn temperatur
temperature_obj = temperature.Temperature()
temperature_obj.closest_station(input_obj.lat, input_obj.long)
temperature_obj.process(temperature_obj.id)

# beregne energibehov
demand_obj = demand.Demand()
demand_obj.from_file(input_obj.area, temperature_obj.id)
demand_obj.update()

# justere forutsetninger
adjust_obj = adjust.Adjust(1.5, demand_obj.space_heating_sum, demand_obj.dhw_sum, 10, 5, 3.0, demand_obj.dhw_arr, demand_obj.space_heating_arr)

# resultater
if adjust_obj.start == True:
    st.title('Resultater')

    # grunnvarmeberegning
    geoenergy_obj = geoenergy.Geoenergy((adjust_obj.dhw_arr + adjust_obj.space_heating_arr), 
    temperature_obj.average_temperature, adjust_obj.cop, adjust_obj.thermal_conductivity, 
    adjust_obj.groundwater_table, adjust_obj.energycoverage)
    