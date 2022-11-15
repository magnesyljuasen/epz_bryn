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