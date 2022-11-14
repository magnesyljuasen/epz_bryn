import streamlit as st
from apps import EPZ  # import your app modules here

st.set_page_config(page_title="EPZ", layout="centered")

EPZ.app()

#test_app