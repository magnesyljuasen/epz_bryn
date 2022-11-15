import streamlit as st
from src.scripts import EPZ  # import your app modules here

st.set_page_config(page_title="EPZ", layout="centered")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


st.title("Energy Plan Zero")
st.header("Velg studieområde")
lat = st.number_input('Lengdegrad', value = 60.3925)
long = st.number_input('Breddegrad', value = 5.3233)
st.title("Scenariobygger")
tab1, tab2, tab3, tab4, tab5 = st.tabs(['1', '2', '3', '4', '5'])
with tab1:
    st.title("Scenario 1")
    EPZ.app(lat, long)


#test_app