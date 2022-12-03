from typing import List
from fastapi import Depends, FastAPI, HTTPException
from . import schemas, utility


app = FastAPI(title="Price scraper")


@app.post("/prices/", response_model=List[schemas.Price])
def get_prices(items: List[schemas.ProductSpec]):
    # returns list of all prices that it has links for 
    prices = utility.get_all_prices(items)
    return prices

@app.get("/prices/", response_model=List[schemas.PriceInfo])
def get_prices():
    prices = utility.get_all_prices2()
    return prices
