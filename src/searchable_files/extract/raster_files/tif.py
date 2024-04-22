from osgeo import gdal, osr

# --------------- for datasource file ------------------#

# "enum GDALColorInterp" from https://www.gdal.org/gdal_8h.html#ace76452d94514561fffa8ea1d2a5968c
GDALColorInterp = {0: 'Undefined', 1: 'Gray', 2: 'Paletted (see color table)', 3: 'Red', 4: 'Green', 5: 'Blue',
                   6: 'Alpha', 7: 'Hue', 8: 'Saturation', 9: 'Lightness', 10: 'Cyan', 11: 'Magenta', 12: 'Yellow',
                   13: 'Black', 14: 'Y Luminance', 15: 'Cb Chroma', 16: 'Cr Chroma', 17: 'Max'}

LOG_PATH = '/tmp/messages.txt'


def getMetadata(filepath):
    data = {}
    datasource = gdal.Open(filepath)
    if datasource is None:
        return None

    try:
        data['xsize'] = datasource.RasterXSize
        data['ysize'] = datasource.RasterYSize

        ulx, uly, llx, lly, lrx, lry, urx, ury = getCoverage(datasource)

        # Get source CRS from dataset
        src_crs = osr.SpatialReference()
        src_crs.ImportFromWkt(datasource.GetProjection())

        # Determine if the source CRS is geographic or projected
        # if src_crs.IsGeographic():
        if True:
            # If geographic, no transformation is needed
            data['northlimit'] = max(uly, lly, lry, ury)
            data['southlimit'] = min(uly, lly, lry, ury)
            data['eastlimit'] = max(ulx, llx, lrx, urx)
            data['westlimit'] = min(ulx, llx, lrx, urx)
        else:
            # If projected, convert to WGS84

            # todo debug the code in this condition
            tgt_crs = osr.SpatialReference()
            tgt_crs.ImportFromEPSG(4326)  # WGS84
            transform = osr.CoordinateTransformation(src_crs, tgt_crs)

            # Transform points
            ulx, uly, _ = transform.TransformPoint([ulx, uly])
            llx, lly, _ = transform.TransformPoint(llx, lly)
            lrx, lry, _ = transform.TransformPoint(lrx, lry)
            urx, ury, _ = transform.TransformPoint(urx, ury)

            # Compute geographic limits
            longitudes = [ulx, llx, lrx, urx]
            latitudes = [uly, lly, lry, ury]
            data['northlimit'] = max(latitudes)
            data['southlimit'] = min(latitudes)
            data['eastlimit'] = max(longitudes)
            data['westlimit'] = min(longitudes)

    except Exception as e:
        with open(LOG_PATH, 'a+') as logfile:
            logfile.write('Exception occurred getting metadata for tif file: ' + str(e))

    return data


def getCoverage(datasource):
    upx, xres, xskew, upy, yskew, yres = datasource.GetGeoTransform()
    cols = datasource.RasterXSize
    rows = datasource.RasterYSize

    ulx = upx + 0 * xres + 0 * xskew
    uly = upy + 0 * yskew + 0 * yres

    llx = upx + 0 * xres + rows * xskew
    lly = upy + 0 * yskew + rows * yres

    lrx = upx + cols * xres + rows * xskew
    lry = upy + cols * yskew + rows * yres

    urx = upx + cols * xres + 0 * xskew
    ury = upy + cols * yskew + 0 * yres

    return ulx, uly, llx, lly, lrx, lry, urx, ury
