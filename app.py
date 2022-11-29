import streamlit as st
from src.scripts import EPZ, input

st.set_page_config(page_title="EPZ", layout="centered")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


st.title("Energy Plan Zero - Sluppen")

#input_obj = input.Input()

#EPZ.app(input_obj.lat, input_obj.long)
EPZ.app(63.397647, 10.399185)


