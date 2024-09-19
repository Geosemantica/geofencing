from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema


class MiningSourceSchema(BaseSchema):
    id: int
    filename: str = Field(validation_alias='name')
    created_at: datetime
