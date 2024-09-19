from dataclasses import dataclass


@dataclass
class RasterCreationAttrs:
    point_set: str
    algorithm: str
    maxx: float
    minx: float
    maxy: float
    miny: float
    resolution: float
    srs: int
    band_type: str = '32BF'
