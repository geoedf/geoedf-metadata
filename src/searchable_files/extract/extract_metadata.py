from . import raster
from . import vector
import os.path


def extract_metadata(filepath):
    root, ext = os.path.splitext(filepath)
    if ext in vector.extensions:
        return vector.getMetadata(filepath)
    elif ext in raster.extensions:
        return raster.getMetadata(filepath)
