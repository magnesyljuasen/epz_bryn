import streamlit as st
from st_keyup import st_keyup
import requests
import time 

class Adjust:
    def __init__(self, elprice, spaceheating, dhw, depth_to_bedrock, groundwater_table, thermal_conductivity, dhw_arr, space_heating_arr):
        self.dhw_arr = dhw_arr
        self.space_heating_arr = space_heating_arr
        self.elprice = elprice
        self.space_heating_old = spaceheating
        self.dhw_old = dhw
        self.energycoverage = 95
        self.depth_to_bedrock = depth_to_bedrock
        self.groundwater_table = groundwater_table
        self.thermal_conductivity = thermal_conductivity
        self.adjust_input()
        self.adjust()

    def adjust_input(self):
        with st.form('input'):
            with st.expander("⚡ Energi og effekt"):
                c1, c2 = st.columns(2)
                with c1:
                    self.spaceheating_f()
                    self.dhw_f()
                with c2:
                    self.heatsystem_f()
                    self.energycoverage_f() 
            with st.expander("🌱 Kostnad- og miljøanalyse"):
                c1, c2 = st.columns(2)
                with c1:
                    self.elprice_f()
                with c2:
                    self.energymix_f()
            with st.expander("⛰️ Grunnforhold"):
                c1, c2 = st.columns(2)
                with c1:
                    self.groundwater_table_f()
                    self.depth_to_bedrock_f()
                with c2:
                    self.thermal_conductivity_f()
            if st.form_submit_button('🖩 Start beregning'):
                self.start = True
            else:
                self.start = False
    
    def heatsystem_f(self):
        option_list = ['Gulvvarme', 'Gulvvarme | Radiator', 'Radiator']
        selected = st.selectbox('Velg type varmesystem', options=option_list)
        x = {option_list[0] : 4, option_list[1] : 3, option_list[2] : 2}
        self.cop = x[selected]

    def elprice_f(self):
        self.elprice = st.number_input('Velg strømpris [kr/kWh]', min_value=0.5, value=self.elprice, max_value=10.0, step=0.1)

    def energymix_f(self):
        option_list = ['Norsk', 'Norsk-europeisk', 'Europeisk']
        selected = st.selectbox('Velg type energimiks for strømproduksjon', options=option_list)
        x = {option_list[0] : 16.2, option_list[1] : 116.9, option_list[2] : 123}
        self.energymix = x[selected]

    def energycoverage_f(self):
        self.energycoverage = st.number_input('Velg energidekningsgrad [%]', min_value=80, value=95, max_value=100)

    def spaceheating_f(self):
        self.space_heating_sum = st.number_input('Juster romoppvarmingsbehov [kWh]', min_value=0, value=self.space_heating_old, max_value=100000, step=1000)

    def dhw_f(self):
        self.dhw_sum = st.number_input('Juster tappevannsbehov [kWh]', min_value=0, value=self.dhw_old, max_value=100000, step=1000)

    def depth_to_bedrock_f(self):
        self.depth_to_bedrock = st.number_input('Dybde til fjell [m]', min_value=0, value=self.depth_to_bedrock, max_value=100, 
        help=''' Dybde til fjell påvirker kostnaden for å 
        bore energibrønn, og kan variere mye fra sted til sted. 
        Brønnborer bør sjekke dette opp mot NGU sine databaser for 
        grunnvannsbrønner og grunnundersøkelser.''')

    def groundwater_table_f(self):
        self.groundwater_table = st.number_input('Dybde til grunnvannspeil [m]', min_value=0, value=self.groundwater_table, max_value=100)

    def thermal_conductivity_f(self):
        self.thermal_conductivity = st.number_input('Effektiv varmeledningsevne [W/m*K]', min_value=2.0, value=self.thermal_conductivity, max_value=10.0, step=0.1)

    def adjust(self):
        dhw_sum = self.dhw_old
        dhw_sum_new = self.dhw_sum

        space_heating_sum = self.space_heating_old
        space_heating_sum_new = self.space_heating_sum
        dhw_percentage = dhw_sum_new / dhw_sum
        space_heating_percentage = space_heating_sum_new / space_heating_sum

        self.dhw_arr = (self.dhw_arr * dhw_percentage).flatten()
        self.space_heating_arr = (self.space_heating_arr * space_heating_percentage).flatten()
        self.energy_arr = (self.dhw_arr + self.space_heating_arr).flatten()







    
