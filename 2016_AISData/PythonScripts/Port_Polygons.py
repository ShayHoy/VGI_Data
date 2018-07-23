''' This code was created to take a csv file of bounding boxes of specific ports ...
 and create individual polygon shapefiles.  Created by S.Hoy, July 2018'''

# Import necessary packages
from shapely import geometry
import pandas as pd
import geopandas as gpd

# Specify out path
fpath = '/home/mapper/VGI_Data/2016_AISData/ProcessedData/PortPolygons'

# Import csv file as pandas dataframe
df = pd.read_csv('/home/mapper/VGI_Data/2016_AISData/AncilaryData/TheCrowd.csv')
# drop any nan values
df = df.dropna()
# itterate across rows to create individual shapefiles
for index, row in df.iterrows():
    # create empty pandas dataframe
    df1 = pd.DataFrame(columns=['Port', 'CrowdType'])
    # set CrowdType from current row
    df1.set_value(0,'CrowdType', row['CrowdType'])
    # set Port value from city and state value of fow
    df1.set_value(0,'Port', row['City'] + '_' + row['State'])
    # define Upper Left bounding point
    UL = geometry.Point(row['UL_LON'], row['UL_LAT'])
    # define Lower Left bounding point
    LL = geometry.Point(row['LL_LON'], row['LL_LAT'])
    # define Upper Right bounding point
    UR = geometry.Point(row['UR_LON'], row['UR_LAT'])
    # define Lower Right bounding point
    LR = geometry.Point(row['LR_LON'], row['LR_LAT'])
    # create list of polygon points (counter clockwise order)
    poly = [UL, UR, LR, LL]
    # create coordinates
    coords = [[p.x, p.y] for p in poly]
    # create polygon from coordinates
    poly = geometry.Polygon(coords)
    # set coordinate reference 4326 = WGS84
    crs = {'init': 'epsg:4326'}
    # create Geodataframe
    gdf = gpd.GeoDataFrame(df1, crs=crs)
    gdf['geometry'] = poly
    # set filename
    fname = str(row['City'] + '_' + row['State'] + '.shp')
    # output to shapefile
    gdf.to_file(fpath +'/' + fname)



