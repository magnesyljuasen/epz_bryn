import streamlit as st
from src.scripts import EPZ, input
from PIL import Image

st.set_page_config(page_title="EPZ", layout="centered")

with open("src/styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

c1, c2 = st.columns([1, 3])
with c1:
    image = Image.open('src/data/Logo.png')
    st.image(image)

with c2:
    st.title("Energibehov - Bryn")


#input_obj = input.Input()

#EPZ.app(input_obj.lat, input_obj.long)
EPZ.app(59.910155, 10.811134)


