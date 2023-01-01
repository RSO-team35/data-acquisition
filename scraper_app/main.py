from typing import List
from fastapi import Depends, FastAPI, HTTPException, status, Response
from . import schemas, utility
import time 


description = "Service for getting prices"
tags_metadata = [
    {
        "name": "prices",
        "description": "Operations with price data"
    },
    {
        "name": "health",
        "description": "Operations checking service health status"
    }
]


app = FastAPI(title="Price scraper", description=description, openapi_tags=tags_metadata, docs_url="/openapi")
app.processing = False
app.rate = -1


# @app.post("/prices/", response_model=List[schemas.Price], tags=["prices"])
# def get_prices(items: List[schemas.ProductSpec]):
#     """
#     Returns list of new prices for products sent
#     """
#     prices = utility.get_all_prices(items)
#     return prices

@app.get("/prices/", response_model=List[schemas.PriceInfo], tags=["prices"])
def get_prices():
    """
    Gets new prices for all products
    """
    app.processing = True
    if app.rate < 0:
        print(f"Getting price conversion rates")
        app.rate = utility.get_rate() # free is only once a day - also updated once a day
    rate = app.rate if app.rate > 0 else 0.93
    prices = utility.get_all_prices2(rate)
    app.processing = False
    return prices


@app.get("/health/liveness", status_code=status.HTTP_200_OK, tags=["health"])
def get_liveness():
    """
    Checks liveness
    """

@app.get("/health/readiness", status_code=status.HTTP_200_OK, tags=["health"])
def get_readiness():
    """
    Checks readiness
    """
    
    


    