import math
import requests
import numpy as np


class Roof():

    def __init__(self, lat, lon, angle, aspect, footprint_area, loss = 14, mountingplace='building'): # ToDo: Skift til free-standing.
        allowed_mountingplace= ['free', 'building']
        if mountingplace not in allowed_mountingplace:
            arcpy.AddMessage(f"""Mountingplace value {mountingplace} 
                             is not valid. Must be equal to
                             {allowed_mountingplace[0]}
                             or {allowed_mountingplace[1]}""")
            raise ValueError
        self.mountingplace= mountingplace
        self.lat= lat
        self.lon= lon
        self.angle= angle
        self.aspect= aspect
        #ToDo: Er det rett at areal/panel er bakt inn i kWp per panel?
        self.kWp_panel= 0.4 #kWp/panel
        self.area_panel= 1.7 #area/panel
        self.area_loss_factor = 0.5 #amout of area not exploitable ToDo: Expose to user
        self.footprint_area= footprint_area
        self.surface_area= self._surface_area()
        self.area_exploitable = self.surface_area * self.area_loss_factor
        self.loss= loss
        self.kwp= self._kwp()
        self.main_url= 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?'
        self.payload= {'lat': lat, 'lon': lon, 'peakpower': self.kwp,
                        'angle': self.angle, 'aspect': self.aspect, 'loss': self.loss,
                        'mountingplace': self.mountingplace,'outputformat':'json',
                       }
        self.pvgisdata = self._pvgisdata()


        # ToDo consider asking for pvprice etc.

    def _surface_area(self):
        angle_r = math.radians(self.angle)
        b = math.sqrt(self.footprint_area)
        hypotenus = b/math.cos(angle_r)
        surface_area = hypotenus * b
        return surface_area

    def _kwp(self):
        """
        se https://www.av-solkalkulator.no/calc
        :return: float, kilowattpeak
        """
        return 1

    def _pvgisdata(self):
        r = requests.get(url= self.main_url, params= self.payload)
        return r.json()


    def E_y(self):
        # ToDo: Vidar sjekk
        """
        Yearly PV energy production [kWh]
        :return: float, kilowatthours per square meter
        """
        # per kilowatt peak
        kWh_m2 = self.pvgisdata['outputs']['totals']['fixed']['E_y']
        return kWh_m2

    def E_y_on_surface(self):
        # ToDo: Vidar sjekk
        """
        Yearly energy production kWh for exploitable surface area
        :return:
        """
        kWh_total = self.pvgisdata['outputs']['totals']['fixed']['E_y']*self.area_exploitable / self.area_panel * self.kWp_panel
        return kWh_total

    def Hi_y(self):
        # ToDo: Vidar sjekk.
        """
        Average annual sum of global irradiation per square meter
        recieved by modules of the given system
        :return: float, kWh/m2/y
        """
        return self.pvgisdata['outputs']['totals']['fixed']['H(i)_y']

    def Hi_y_on_surface(self):
        #ToDo: Vidar sjekk. Viss rett, skal vi bruke totalt areal eller expl surf
        """
        H(i)_y average per year for roof surface
        :return:
        """
        return self.pvgisdata['outputs']['totals']['fixed']['H(i)_y'] * self.surface_area

def ScriptTool(itemid):
    # Script execution code goes here

    def get_hostefeaturelayerdata(itemid):
        gis = GIS(url='https://asplanviak.maps.arcgis.com',
                  username='torbjorn.boe_asplanviak',
                  password='Maskinlæring for maskiner 50')
        bygg_item = gis.content.get(itemid)
        bygg_fl = bygg_item.layers[0]
        return bygg_fl

    def get_centroids(bygg_fset):
        try:
            centroids = {feature.attributes['OBJECTID']: feature.attributes['centroid'] for feature in
                         bygg_fset.features}
        except KeyError as e:
            print(
                f'Check if return centroid is True on featurelayerquery. Check if fieldname OBJECTID exists. KeyError on {e}')
        return centroids

    def project_centroids(centroids, from_sr=25832, to_sr=4326):
        projected = {}
        for k, v in centroids.items():
            v['spatialReference'] = {"wkid": 25832}
            point = geometry.Point(v)
            reprojected = geometry.project([point], in_sr=from_sr, out_sr=to_sr)
            projected[k] = reprojected[0]
        return projected

    def update_byggpunkt_solenergi(featurelayer, scenarionummer = None):
        takflate_bokstav= ['A', 'B', 'C', 'D']
        bygg_fset = featurelayer.query(return_centroid=True)
        bygg_features = bygg_fset.features
        centroids = project_centroids(get_centroids(bygg_fset))
        if scenarionummer:
            updates = [f for f in bygg_features if f.attributes['Scenarionummer'] == scenarionummer]
        else:
            updates = [f for f in bygg_features]
        for bygg_feature in updates:
            attributes = bygg_feature.attributes
            if not attributes['Takflater_vinkel']:
                roof_angle = 25 #Vinkel på tak settes default
            else:
                roof_angle = attributes['Takflater_vinkel']
            E_y_pr_roof = []
            Hi_y_pr_roof = []
            for bokstav in takflate_bokstav:
                area_field = f'Takflate_{bokstav}_areal'
                aspect_field= f'Takflate_{bokstav}_orientering'
                x = centroids[attributes['OBJECTID']]['x']
                y = centroids[attributes['OBJECTID']]['y']
                aspect = attributes[aspect_field]
                footprint_area = attributes[area_field]
                if footprint_area and aspect is not None:
                    roof = Roof(lat=y, lon=x, angle=roof_angle,
                                aspect=aspect, footprint_area=footprint_area)
                    E_y_on_surface = roof.E_y_on_surface()
                    Hi_y_on_surface = roof.Hi_y_on_surface()
                    E_y_pr_roof.append(E_y_on_surface)
                    Hi_y_pr_roof.append(Hi_y_on_surface)
                    attributes[f'Takflate_{bokstav}_solenergi_y'] = E_y_on_surface
                    attributes[f'Takflate_{bokstav}_solinnstråling_y'] = Hi_y_on_surface
                    attributes[f'Takflate_{bokstav}_overflateareal'] = roof.surface_area
                    arcpy.AddMessage(f'takflate {bokstav}: E_y_on_surface: {E_y_on_surface}, H(i)_y: {Hi_y_on_surface}, kwp: {roof.kwp}, sarea: {roof.surface_area}')
            attributes['Sum_solenergi_y']= sum(E_y_pr_roof)
            attributes['Sum_solinnstråling_y'] = sum(Hi_y_pr_roof)
        featurelayer.edit_features(updates= updates)

    featurelayer= get_hostefeaturelayerdata(itemid= itemid)
    update_byggpunkt_solenergi(featurelayer= featurelayer)
