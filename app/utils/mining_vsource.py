from geopandas import GeoDataFrame, read_file
from shapely import MultiPoint, Point
from shapely.ops import transform

from app.exceptions import InvalidFileError
from common.enums import MiningAreaType


class MiningAreaVectorSource:
    def __init__(self, gdf: GeoDataFrame, path=None):
        self.gdf = gdf
        self.path = path

    @classmethod
    def read_file(cls, path, attrs=None):
        if attrs is None:
            attrs = ['geometry', 'Layer']
        try:
            gdf = read_file(path)[attrs]
        except Exception as e:
            raise InvalidFileError(f'Invalid file {str(e)}')
        return cls(gdf, path)

    def validate(self):
        for layer in self.gdf['Layer'].unique():
            if layer.split('_')[0] in MiningAreaType.types():
                break
        else:
            raise InvalidFileError(f'No layer with source type: {MiningAreaType.types()}')

    def filter_triangles(self):
        self.gdf = self.gdf.loc[self.gdf['geometry'].geom_type == 'Polygon']
        self.gdf = self.gdf[self.gdf.geometry.apply(lambda geom: len(geom.exterior.coords) == 4)]

    def transform(self, pre_offset: tuple[float], s_srs=28415, t_srs=4326):
        self.gdf.geometry = self.gdf.translate(*pre_offset)
        self.gdf.crs = f'EPSG:{s_srs}'
        self.gdf.to_crs(f'EPSG:{t_srs}', inplace=True)

    def get_layers(self) -> list[str]:
        return [layer for layer in self.gdf['Layer'].unique() if layer.split('_')[0] in MiningAreaType.types()]

    def get_2d_polygon_from_layer(self, layer: str):
        return transform(lambda x, y, z=None: (x, y), self.gdf[self.gdf['Layer'] == layer].unary_union)

    def get_points_from_layer(self, layer: str) -> MultiPoint:
        points = set()
        for polygon in self.gdf[self.gdf['Layer'] == layer].geometry:
            points.update([Point(x, y, z) for x, y, z in polygon.exterior.coords[:-1]])
        return MultiPoint(tuple(points))
