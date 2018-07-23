def PortSubsetByMonth (aisfile, polyfile, port,  month, chunksize=200000):
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
    import pandas as pd
    import matplotlib.pyplot as plt

    outpath = '/home/mapper/VGI_Data/2016_AISData/ProcessedData/Port_AIS' + '/' + port + '/'
    fname = port + '_' + month

    port = gpd.read_file(polyfile)
    poly = port['geometry']
    fields = ['MMSI', 'LAT', 'LON', 'VesselType', 'Length', 'Width', 'Draft']
    df = pd.DataFrame(columns=fields)

    for chunk in pd.read_csv(aisfile, chunksize=chunksize, usecols=fields):
        chunk = chunk.dropna(subset=['VesselType', 'Draft'])
        chunk = chunk.reset_index(drop=True)
        points = gpd.GeoSeries(Point(xy) for xy in zip(chunk.LON, chunk.LAT))
        within = points.within(poly.iloc[0])
        chunk_small = chunk[within]
        df = df.append(chunk_small, ignore_index=True)

    df.to_csv(outpath + fname + '.csv')

    points_small = gpd.GeoSeries(Point(xy) for xy in zip(df.LON, df.LAT))
    base = poly.plot(color='white', edgecolor='red')
    points_small.plot(ax=base, marker='o', color='black')
    plt.show()

def CombineMonths (folder, port):
    import os
    import pandas as pd

    r = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            r.append(os.path.join(root, name))

    allDF = pd.DataFrame()
    for file in r:
        df = pd.read_csv(file)
        allDF = allDF.append(df)

    outpath = folder + '/' + port
    allDF.to_csv(outpath + '_ALL2016.csv')
    print('Finished ' + port)




