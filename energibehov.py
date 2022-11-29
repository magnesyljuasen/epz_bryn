import pandas as pd
import numpy as np
import pathlib
import os
from matplotlib import pyplot as plt

class Energibehov:
    def __init__(self):
        this_location = pathlib.Path(__file__)
        self.profet_data = pd.read_csv('src/data/Effektprofiler.csv', sep=';')
        
    def hent_profil(self, bygningstype, bygningsstandard, forbrukstype, areal):
        bygningstype, bygningsstandard, forbrukstype, areal = self.input_data(bygningstype, bygningsstandard, forbrukstype, areal)
        if forbrukstype == 'Space_heating_og_DHW':
            return areal * (np.array(self.profet_data[bygningstype + bygningsstandard + 'Space_heating']) + np.array(self.profet_data[bygningstype + bygningsstandard + 'DHW']))
        else:
            return areal * np.array(self.profet_data[bygningstype + bygningsstandard + forbrukstype])
            
    def input_data(self, bygningstype, bygningsstandard, forbrukstype, areal):
        #bygningstype = bygningstype.upper()
        #bygningsstandard = bygningsstandard.upper()
        #forbrukstype = forbrukstype.upper()

        bygningstyper = {
            'A' : 'House', 
            'B' : 'Apartment', 
            'C' : 'Office', 
            'D' : 'Shop', 
            'E' : 'Hotel',
            'F' : 'Kindergarten',
            'G' : 'School', 
            'H' : 'University',
            'I' : 'Culture_Sport', 
            'J' : 'Nursing_Home',
            'K' : 'Hospital',
            'L' : 'Other', 
        }
        bygningsstandarder = {
            'X' : 'Regular',
            'Y' : 'Efficient',
            'Z' : 'Very efficient',
        }
        forbrukstyper = {
            '1' : 'Electric',
            '2' : 'DHW',
            '3' : 'Space_heating',
            '4' : 'Cooling',
            '5' : 'Space_heating_og_DHW',
        }
        return bygningstyper[bygningstype], bygningsstandarder[bygningsstandard], forbrukstyper[forbrukstype], areal




