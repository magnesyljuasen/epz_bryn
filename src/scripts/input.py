import streamlit as st
from st_keyup import st_keyup
import requests
import time 

class Input:
    def __init__(self):
        selected_adr, selected_lat, selected_long, selected_postcode = self.address_input()
        if selected_adr != 0:
            self.area_input()
            self.adr = selected_adr
            self.lat = selected_lat
            self.long = selected_long
            self.postcode = selected_postcode

    def address_search(self, adr):
        options_list = []
        lat_list = []
        long_list = []
        postnummer_list = []
        r = requests.get(f"https://ws.geonorge.no/adresser/v1/sok?sok={adr}&fuzzy=true&treffPerSide=6&sokemodus=OR", auth=('user', 'pass'))
        if r.status_code == 200 and len(r.json()["adresser"]) == 6:   
            for i in range(0, 6):
                json = r.json()["adresser"][i]
                adresse_tekst = json["adressetekst"]
                poststed = (json["poststed"]).capitalize()
                postnummer = json["postnummer"]
                postnummer_list.append(postnummer)
                opt = f"{adresse_tekst}, {poststed}"
                options_list.append(opt)
                lat_list.append(json["representasjonspunkt"]["lat"])
                long_list.append(json["representasjonspunkt"]["lon"])
        return options_list, lat_list, long_list, postnummer_list
    
    def address_input(self):
        st.title("Hvor befinner boligen seg?")
        adr = st_keyup("📍 Skriv inn adresse", key="adresse1")
        if len(adr) == 0:
            st.write('FORSIDE')
        options_list, lat_list, long_list, postcode_list = self.address_search(adr)
        c1, c2 = st.columns(2)
        if len(options_list) == 0:
            st.stop()
        elif len(options_list) > 0:
            with c1:
                s1 = st.checkbox(options_list[0])
                s2 = st.checkbox(options_list[1])
                s3 = st.checkbox(options_list[2])
            with c2:
                s4 = st.checkbox(options_list[3])
                s5 = st.checkbox(options_list[4])
                s6 = st.checkbox(options_list[5])
            if s1 == False and s2 == False and s3 == False and s4 == False and s5 == False and s6 == False:
                index = -1
            elif s1 == False and s2 == False and s3 == False and s4 == False and s5 == False and s6 == True:
                index = 5
            elif s1 == False and s2 == False and s3 == False and s4 == False and s5 == True and s6 == False:
                index = 4
            elif s1 == False and s2 == False and s3 == False and s4 == True and s5 == False and s6 == False:
                index = 3
            elif s1 == False and s2 == False and s3 == True and s4 == False and s5 == False and s6 == False:
                index = 2
            elif s1 == False and s2 == True and s3 == False and s4 == False and s5 == False and s6 == False:
                index = 1
            elif s1 == True and s2 == False and s3 == False and s4 == False and s5 == False and s6 == False:
                index = 0
            else:
                st.error("Du kan kun velge én adresse!", icon="🚨")
                st.stop()
            
            if index != -1:
                selected_adr = options_list[index]
                selected_lat = lat_list[index]
                selected_long = long_list[index]
                selected_postcode = postcode_list[index]
            else:
                selected_adr = 0
                selected_lat = 0
                selected_long = 0
                selected_postcode = 0
                st.stop()
            return selected_adr, selected_lat, selected_long, selected_postcode

    def area_input(self):
        st.title("Hvor stor er boligen?")
        selected_area = st_keyup(f"🏠 Tast inn oppvarmet boligareal [m\u00B2]", key="areal2")
        if len(selected_area) == 0:
            st.markdown('---')
            st.stop()
        else:
            if not selected_area.isnumeric():
                st.error("Input må være tall!", icon="🚨")
                st.markdown("---")
            elif len(selected_area) > 0 and int(selected_area) < 100 or int(selected_area) > 500:
                time.sleep(2)
                st.error("Oppvarmet boligareal må være mellom 100 og 500 m\u00b2", icon="🚨")
            elif len(selected_area) > 0 and int(selected_area) >= 100 and int(selected_area) <= 500:
                self.area = int(selected_area)
