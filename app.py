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
