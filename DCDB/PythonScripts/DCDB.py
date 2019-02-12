def DCDB_toPoints(folder):

    ''' This function takes the raw DCDB CSB geojson files (within a folder,    which most of the time is unique to a
    vessel), removes entries with missing depth or positioning information, or timestamps out of an acceptable range.
    It then prints the number of removed points for missing depth values, positioning values, and timestamps. It exports
    the data as a shapefile.

    It may be necessary to process large files by chunksize depending on your computer specs.

    If you have any questions contact: Shannon Hoy @ shoy@ccom.unh.edu'''

    ## Import necessary packages

    import geopandas as gpd
    import os
    import json

    # Set up folder to walk through containing multiple files for unique ROSEP IDs.. typically unique to one vessel,...
    # but not always
    count = 0
    r = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            filename_wo_extension, extension = os.path.splitext(name)
            if extension == '.json':
                count += 1
                r.append(os.path.join(root, name))

    # Set directory to save shapefile
    outdir = '/home/mapper/VGI_Data/DCDB/CSB_DATA/ProcessedData/Points'

    # Set empty geodataframe
    GDF = gpd.GeoDataFrame(columns=['depth', 'time', 'geometry', 'filename', 'shipname', 'shiplength', 'shiptype'])

    # Read geojson files
    for file in r:
        count += 1
        filepath = str(file)
        gdf = gpd.read_file(filepath)
        # set coordinate reference system to WGS84
        gdf.crs = {'init': 'epsg:4326'}
        GDF = GDF.append(gdf, ignore_index=True)
        GDF.crs = {'init': 'epsg:4326'}

    # Load geojson file
    rawjson = json.loads(open(file).read())
    # extract ship name
    shipname = rawjson["properties"]["platform"]["name"]
    GDF['shipname'] = shipname
    # extract ship length
    GDF['shiplength'] = rawjson["properties"]["platform"]["length"]
    # extract ship type
    GDF['shiptype'] = rawjson["properties"]["platform"]["type"]
    # extract file name (ROSEPOINT ID)
    GDF['filename'] = os.path.basename(file)

    # Remove special characters from shipname
    shipname_nospecial = shipname.translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})
    # Replace space in shipname with underscore
    shipname_nospecial = shipname_nospecial.replace(" ", "_")

    # Set up geodataframe with Latitude/Longitdue
    GDF['latitude'] = GDF.geometry.apply(lambda p: p.y)
    GDF['longitude'] = GDF.geometry.apply(lambda p: p.x)

    # Get time in format to work with
    GDF['time'] = GDF['time'].astype(str)
    GDF['year'] = GDF.time.str[:4]
    GDF['year_month_day'] = GDF.time.str[:10]

    # Make depths negative
    GDF['depth'] = GDF['depth'] * -1

    # Organize Geodataframe
    GDF = GDF[['filename', 'shipname', 'shiplength', 'shiptype', 'time', 'year', 'year_month_day', 'latitude', 'longitude',
               'depth', 'geometry']]

    # Set acceptable dates for timestamp
    acceptable_dates = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010',
                        '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

    # Count the beginning number of points before removing blunders
    total_pts = GDF['depth'].count()

    # Remove depths that are 0 or positive
    GDF = GDF[GDF.depth != 0]
    GDF = GDF[GDF.depth < 0]
    total_pts_depth_filter = GDF['depth'].count()
    # Count the number of removed points
    removed_depths = total_pts - total_pts_depth_filter

    # Remove 0 entries for latitude and longitude
    GDF = GDF[GDF.latitude != 0]
    GDF = GDF[GDF.longitude != 0]
    total_pts_position_filter = GDF['depth'].count()
    # Count the number of removed position points
    removed_position = total_pts - total_pts_position_filter - removed_depths

    # See if the Year of the data is in the acceptable range
    GDF = GDF[GDF['year'].isin(acceptable_dates)]
    total_pts_time_filter = GDF['depth'].count()
    # Remove entries with timestamps not in the acceptable range
    removed_time = total_pts - total_pts_time_filter - removed_depths - removed_position

    # List the unique years represented in the data
    year = GDF['year'].unique()
    # List the unique days represented in the data
    total_days = GDF['year_month_day'].nunique()

    # Count the final points after removing the blundered entries
    finalpts = GDF['depth'].count()

    # Print the results
    print('years active = ' + str(year))
    print('Total Days Active = ' + str(total_days))
    print('The total number of files for ' + shipname + ' is: ' + str(count))
    print('The total number of points ' + shipname + ' is: ' + str(total_pts))
    print('The total number of removed depths ' + shipname + ' is: ' + str(removed_depths))
    print('The total number of removed positions ' + shipname + ' is: ' + str(removed_position))
    print('The total number of removed time ' + shipname + ' is: ' + str(removed_time))
    print('The final number of points ' + shipname + ' is: ' + str(finalpts))

    # Export the processed points to a shapefile
    GDF.to_file(driver="ESRI Shapefile", filename=outdir + '/' + shipname_nospecial + '_' + '%s.shp' % count)

    print('Finished Exporting Shapefile')
