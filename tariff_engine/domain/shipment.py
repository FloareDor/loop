from pydantic import BaseModel, Field


class Shipment(BaseModel):
    weight: float = Field(gt=0)
    zone: int = Field(ge=1)
    origin_zip: str = ""
    dest_zip: str = ""
    service_type: str = "ground"
