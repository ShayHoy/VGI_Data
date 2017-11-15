import pandas as pd
import geopandas as gpd

fp = '/home/mapper/VGI_Data/SeaID/csb3/20130829.log'
data = pd.read_csv(fp, sep='|', names=['Epoch', 'Depth', 'Lat', 'Long'])
