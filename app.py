import streamlit as st
from src.scripts import EPZ, input

st.set_page_config(page_title="EPZ", layout="centered")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


st.title("Energy Plan Zero")
st.header("Velg studieområde")
st.caption("TO DO: Avgrens område med et polygon")
#input_obj = input.Input()
st.title("Scenariobygger")

#EPZ.app(input_obj.lat, input_obj.long)
EPZ.app(63.452757, 10.446476)


# Struktur
# Klasser:

# BuildMap
# Velg studieområde ut ifra lokasjonsinput. Kan være adresse, område. 
# Plassere ut bygg i kart, og gi parametere. 
# Kan også velge å legge inn shape-filer. Ta inn WMS-tjenester. Ta inn data. 
# Kartet og spatialdataframe med bygninger returneres til app.py. Hvordan løser vi PROFet?
# Kunne kjørt den med "other"?

# EnergyDemand
# Ta inn spatial dataframe, og beregn energibehov for hvert bygg og totalt. 
# Mulighet til å endre behovet for hvert bygg (laste opp separate profiler).
# Kanskje en overklasse her som heter Building(EnergyDemand). Returnere, nedlaste og
# Visualisere lastprofiler og effekter. 

#-- 
# GeoEnergy
# Input er termisk energibehov. Kan muligens anta en 80 kWh/m for dimensjonering av brønnene eventuelt
# bruke pygfunction eller 80 kWh/m.

# Solar
# bruke pvgis

# AirSourceHeatPump
# ta inn COP, og lastprofiler. 

# SeaWaterHeatPump
# COP 

#--
