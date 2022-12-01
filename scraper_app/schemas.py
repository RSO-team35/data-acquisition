from typing import Union, List
from pydantic import BaseModel, HttpUrl
import datetime


class Price(BaseModel):
    price: float
    date: datetime.datetime
    retailer: str
    manufacturer: str

    class Config:
        orm_mode = True


class ProductSpec(BaseModel):
    retailer: str # could create custom type
    manufacturer: str
    model: str # Zotac Gaming etc
    name: str # Nvidia RTX 3060 Ti, this is a product name
    url: HttpUrl

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "retailer": "Mimovrste",
                "manufacturer": "ASUS",
                "model": "ASUS ROG Strix",
                "name": "NVIDIA RTX 3090",
                "url": "https://www.mimovrste.com/graficne-kartice-nvidia/asus-rog-strix-gaming-oc-geforce-rtx-3090-graficna-kartica-24-gb-gddr6x",
            }
        }

