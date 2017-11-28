def SeaID_toPandas(VesselID, filename):
    import pandas as pd
    import numpy as np
    import os

    # Parse Log File
    fp = filename
    data = pd.read_csv(fp, sep='|', names=['Epoch', 'Depth', 'Lat', 'Long'])

    # Add Vessel ID Column
    data.insert(0, 'VesselID', VesselID)

    # Add FileName Column
    FileNameTemp = os.path.splitext(fp)[0]
    FileName = FileNameTemp[-8:]
    data.insert(1, 'FileName', FileName)


    # Remove observations with empty cells
    data.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    data.dropna(inplace=True)

    # Convert Latitude to Usable Format

    data['LatTemp'] = data['Lat'].str.split(' ').str.get(0)
    data['LongTemp'] = data['Long'].str.split(' ').str.get(0)

    data['LatN'] = pd.to_numeric(data['LatTemp'].str[0:2]) + (pd.to_numeric(data['LatTemp'].str[2:]) / 60)
    data['LongN'] = pd.to_numeric(data['LongTemp'].str[0:3]) + (pd.to_numeric(data['LongTemp'].str[3:]) / 60)

    # Convert Latitude to Usable Format
    conditionsLat = [
        (data['Lat'].str.split(' ').str.get(1) == 'N'),
        (data['Lat'].str.split(' ').str.get(1) == 'S')]

    choicesLat = [data['LatN'],
                  -1 * data['LatN']]
    data['LatDD'] = np.select(conditionsLat, choicesLat, default=np.nan)

    # Convert Longitude to Usable Format
    conditionsLong = [
        (data['Long'].str.split(' ').str.get(1) == 'E'),
        (data['Long'].str.split(' ').str.get(1) == 'W')]

    choicesLong = [data['LongN'],
                   -1 * data['LongN']]
    data['LongDD'] = np.select(conditionsLong, choicesLong, default=np.nan)

    if 'Lat' in data.columns:
        data = data.drop(['Lat', 'Long', 'LatTemp', 'LongTemp', 'LatN', 'LongN'], axis=1)

    return data

def SeaID_toGeoPandas(pandasDF):
    import geopandas as gpd
    from shapely.geometry import Point, LineString
    # Convert pandas to geodataframe

    pandas = pandasDF.copy(deep=True)
    geometry = [Point(xy) for xy in zip(pandas.LongDD, pandas.LatDD)]

    # Set Coordinate System to WGS84
    crs = {'init': 'epsg:4326'}
    geoData = gpd.GeoDataFrame(pandas, crs=crs, geometry=geometry)
    # Make LineString DataFrame
    geoData = geoData.groupby(['FileName'])['geometry'].apply(lambda x: LineString(x.tolist()))
    geoDataLine = gpd.GeoDataFrame(geoData, geometry='geometry', crs=crs).reset_index()

    return geoDataLine

def processDir(DirPath):
    import pandas as pd
    import geopandas as gpd
    import os

    direc = DirPath + '/'
    vesselID = os.path.basename(DirPath)
    DATA = pd.DataFrame(columns=['VesselID', 'FileName', 'Epoch', 'Depth', 'LatDD', 'LongDD'])
    GEODATA = gpd.GeoDataFrame(columns=['FileName', 'geometry'])

    files = os.listdir(DirPath)
    numFiles = len(files)
    i = 0
    for f in files:
        filepath = os.path.join(direc, f)
        data = SeaID_toPandas(vesselID, filepath)
        geoDataLine = SeaID_toGeoPandas(data)
        DATA = DATA.append(data)
        GEODATA = GEODATA.append(geoDataLine)
        i = i + 1
        print(f + ' processed ' + str(i) + ' of ' + str(numFiles))

    outDir = '/home/mapper/VGI_Data/ProcessedData'
    outNameCSV = '%s.csv' % vesselID
    outPathCSV = os.path.join(outDir, outNameCSV)
    DATA.to_csv(outPathCSV, columns=['VesselID', 'FileName', 'Epoch', 'Depth', 'LatDD', 'LongDD'], index=False)

    outNameSHP = '%s.shp' % vesselID
    outPathSHP = os.path.join(outDir, outNameSHP)
    GEODATA.to_file(outPathSHP)






