from typing import Annotated

from geoalchemy2.shape import to_shape
from pydantic import BeforeValidator

type wkt = Annotated[str, BeforeValidator(lambda g: to_shape(g).wkt)]
