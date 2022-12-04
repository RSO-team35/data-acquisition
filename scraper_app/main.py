from typing import List
from fastapi import Depends, FastAPI, HTTPException
from . import schemas, utility


description = "Service for getting prices"
tags_metadata = [
    {
        "name": "prices",
        "description": "Operations with price data"
    }
]


app = FastAPI(title="Price scraper", description=description, openapi_tags=tags_metadata)


@app.post("/prices/", response_model=List[schemas.Price], tags=["prices"])
def get_prices(items: List[schemas.ProductSpec]):
    """
    Returns list of new prices for products sent
    """
    prices = utility.get_all_prices(items)
    return prices

@app.get("/prices/", response_model=List[schemas.PriceInfo], tags=["prices"])
def get_prices():
    """
    Gets new prices for all products
    """
    prices = utility.get_all_prices2()
    return prices
