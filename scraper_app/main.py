from typing import List
from fastapi import Depends, FastAPI, HTTPException, status, Response
from . import schemas, utility
import time 
from starlette_prometheus import metrics, PrometheusMiddleware

from . import config

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
app.processing = False # if we do a long operation
app.rate = -1

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics/", metrics)


@app.get("/prices/", response_model=List[schemas.PriceInfo], tags=["prices"])
async def get_prices():
    """
    Gets new prices for all products
    """
    app.processing = True
    if app.rate < 0:
        print(f"Getting price conversion rates")
        app.rate = utility.get_rate() # free is only once a day - also updated once a day
    rate = app.rate if app.rate > 0 else 0.93
    prices = await utility.get_all_prices2(rate)
    app.processing = False
    return prices


@app.get("/price/{product_name}/", response_model=schemas.PriceInfo, tags=["prices"])
def get_price(product_name: str):
    """
    Gets new price for specified product (currently example hardoced for testing!)
    """
    price = utility.get_price(product_name)
    return price


@app.get("/health/liveness/", status_code=status.HTTP_200_OK, tags=["health"])
async def get_liveness():
    """
    Checks liveness
    """
    print("current config:")
    print(config.data_keeping_ip)
    print(config.test_outage)


@app.get("/health/readiness/", status_code=status.HTTP_200_OK, tags=["health"])
async def get_readiness():
    """
    Checks readiness
    """
    
# health - timeouts?  - if there is no internet access or website is down?


    
