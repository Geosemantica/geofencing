import geopandas as gpd
from pyproj import Transformer, CRS
from shapely import buffer, transform
from shapely.geometry.polygon import Polygon
from shapely.ops import transform as proj_transform

from app.exceptions import InvalidFileError


def read_polygon_from_file(path: str) -> Polygon:
    gdf = gpd.read_file(path)
    try:
        return Polygon(gdf.geometry.iloc[0].coords)
    except IndexError:
        raise InvalidFileError(details='No geometry in dataset')


def translate(shape, pre_shift: dict):
    shape = transform(shape, lambda x: x + (pre_shift['x'], pre_shift['y']))
    return shape


def reproject(shape, s_srs=28415, t_srs=4326):
    s_srs = CRS(s_srs)
    t_srs = CRS(t_srs)

    transformer = Transformer.from_crs(s_srs, t_srs, always_xy=True)

    return proj_transform(transformer.transform, shape)


def make_buffer(geom, distance):
    return buffer(geom, distance)
