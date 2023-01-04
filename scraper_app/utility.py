from . import schemas
from . import config
from typing import List
from pydantic import HttpUrl
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree as et
import os
import random
from prometheus_client import Counter


fails = Counter("price_failures", "number of errors when getting updated price", labelnames=["retailer", "result"])


def get_rate():
    try:
        response = httpx.get("https://open.er-api.com/v6/latest/USD")
        if response.status_code != 200:
            return -1
        rates = response.json()["rates"]
    except:
        return -1
    print(f"Got conversion rate from USD to EUR: {rates['EUR']}")
    return rates["EUR"]


def get_all_prices(items: List[schemas.ProductSpec]) -> List[schemas.Price]:
            
    prices = []
    for item in items:
        if item.retailer == "Mimovrste":
            item_price = get_price_mimovrste(item)
            prices.append(item_price)
        elif item.retailer == "Amazon":
            item_price = get_price_amazon(item)
            prices.append(item_price)
        elif item.retailer == "Microcenter":
            item_price = get_price_microcenter(item)
            prices.append(item_price)
        else:
            print(f"Incorrect retailer name: {item.retailer}")
    return prices


async def get_all_prices2(rate):
    # get links
    try:
        data_keeping_ip = config.data_keeping_ip
    except:
        data_keeping_ip = "0.0.0.0:8000"
        assert 0, "No env variable"

    headers = {
    'accept': 'application/json',
    }
    print("getting urls")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{data_keeping_ip}/products/urls/", headers=headers)
    urls = response.json()

    print("getting prices")
    prices = []
    for u in urls:
        print("-"*30)
        item = schemas.ProductSpec(**u)

        if item.retailer == "Mimovrste":
            item_price = get_price_mimovrste(item)
        elif item.retailer == "Amazon":
            item_price = get_price_amazon(item)
        elif item.retailer == "Microcenter":
            item_price = get_price_microcenter(item, rate)
        else:
            print(f"Incorrect retailer name: {item.retailer}")
        
        print(item_price)
        if item_price.price > 0:
            fails.labels(item.retailer, "sucess").inc()
        else:
            fails.labels(item.retailer, "fail").inc()
        price = schemas.PriceInfo(model=item.model, name=item.name, price=item_price.price, date=item_price.date, retailer=item_price.retailer, manufacturer=item_price.manufacturer)
        prices.append(price)
    #print(prices)
    return prices


fails_test = Counter("price_failures_test", "If there was an error when getting updated price", labelnames=["retailer", "result"])

def get_price(product_name=None):
    # placeholder
    p = round(300 + random.uniform(-30, 30), 2)
    if p < 300:
        fails_test.labels("Mimovrste", "sucess").inc()
    else:
        fails_test.labels("Mimovrste", "fail").inc()
    price = schemas.PriceInfo(model="Dual", name="GeForce RTX 3060", price=p, date=datetime.now(), retailer="Mimovrste", manufacturer="ASUS")
    return price 


def get_price_mimovrste(item: schemas.ProductSpec):
    print(f"getting price from mimovrste for {item.name}")
    price_item = schemas.Price(price=-1.0, 
                                date=datetime.now(), 
                                retailer=item.retailer, 
                                manufacturer=item.manufacturer)
    try:
        response = httpx.get(item.url)
        if response.status_code != 200:
            print(f"Response: {response.status_code}")
            return price_item

        soup = BeautifulSoup(response.text, "lxml")
        price_container = soup.find(class_="price__wrap__box__final", recursive=True) # price container on mimovrste - double underscores!!
        price_text = price_container.find("span").text
        price = price_text.strip("\n \xa0€").replace('.','').replace(",", ".") # remove newlines and currency characters and localize number
        price = float(price)
        print(price)
        availability = soup.find(class_="availability-box").text
        if "Trenutno ni na zalogi" in availability:
            price = -1

        price_item.price = price
    except:
        return price_item

    return price_item


def get_price_amazon(item: schemas.ProductSpec):
    print(f"getting price from amazon for {item.name}")
    price_item = schemas.Price(price=-1, 
                                date=datetime.now(), 
                                retailer=item.retailer, 
                                manufacturer=item.manufacturer)

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
        response = httpx.get(item.url, headers=headers)
        print(response.status_code)
        if response.status_code != 200:
            print(f"Response: {response.status_code}")
            return price_item

        #print(response.text)
        soup = BeautifulSoup(response.text, "lxml")
        #print(soup)
        price_container = soup.find(class_="a-offscreen", recursive=True) # price container on amazon
        print(price_container)
        price = price_container.text
        print(price)
        if price is None:
            price_item.price = -1
        else:
            price = price.strip("\n \xa0€").replace(',','').replace('.','') # remove newlines and currency characters and localize number
            price = float(price)
            price /= 100 # sometimes , and . are swapped so just use cents
            print(f"final price: {price}")
            price_item.price = price 

    except Exception as e:
        print(e)
        return price_item

    return price_item


def get_price_microcenter(item: schemas.ProductSpec, rate: float):
    print(f"getting price from amazon for {item.name}")
    price_item = schemas.Price(price=-1, 
                                date=datetime.now(), 
                                retailer=item.retailer, 
                                manufacturer=item.manufacturer)

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
        response = httpx.get(item.url, headers=headers)
        if response.status_code != 200:
            print(f"Response: {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "lxml")
        price_container = soup.find("div", {"class":"product-header"}, recursive=True) # price container on amazon - double underscores!!
        #print(price_container)
        price_text = price_container.find("span").get("data-price")
        #print(price_text)
        if price_text is None:
            price_item.price = -1
        else:
            price = price_text.strip("\n \xa0$").replace(',','').replace('.','') # remove newlines and currency characters and localize number
            price = float(price)
            price /= 100

            print(f"final price: {price} USD")
            # convert to USD
            price = round(price*rate, 2)
            print(f"Price: {price} EUR")
            price_item.price = price 

    except:
        return price_item

    return price_item
