from . import schemas
from typing import List
from pydantic import HttpUrl
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree as et
import os


def get_all_prices(items: List[schemas.ProductSpec]) -> List[schemas.Price]:
            
    prices = []
    for item in items:
        if item.retailer == "Mimovrste":
            item_price = get_price_mimovrste(item)
            prices.append(item_price)
        elif item.retailer == "Amazon":
            item_price = get_price_amazon(item)
            prices.append(item_price)
        else:
            print(f"Incorrect retailer name: {item.retailer}")
    return prices


def get_all_prices2():
    # get links
    data_keeping_ip = os.environ["data_keeping_ip"]
    headers = {
    'accept': 'application/json',
    }
    response = requests.get(f"http://{data_keeping_ip}/products/urls/", headers=headers)
    urls = response.json()

    prices = []
    for u in urls:
        item = schemas.ProductSpec(**u)

        if item.retailer == "Mimovrste":
            item_price = get_price_mimovrste(item)
        elif item.retailer == "Amazon":
            item_price = get_price_amazon(item)
        else:
            print(f"Incorrect retailer name: {item.retailer}")

        price = schemas.PriceInfo(model=item.model, name=item.name, price=item_price.price, date=item_price.date, retailer=item_price.retailer, manufacturer=item_price.manufacturer)
        prices.append(price)
    print(prices)
    return prices


    


def get_price_mimovrste(item: schemas.ProductSpec):
    print(f"getting price from mimovrste for {item.name}")
    price_item = schemas.Price(price=-1.0, 
                                date=datetime.now(), 
                                retailer=item.retailer, 
                                manufacturer=item.manufacturer)
    try:
        response = requests.get(item.url)
        if not response.ok:
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
        response = requests.get(item.url, headers=headers)
        if not response.ok:
            print(f"Response: {response.status_code}")
            return price_item
        soup = BeautifulSoup(response.text, "lxml")
        price_container = soup.find(class_="a-offscreen", recursive=True) # price container on amazon
        price_text = price_container.text
        
        if price is None:
            price_item.price = -1
        else:
            price = price_text.strip("\n \xa0€").replace(',','') # remove newlines and currency characters and localize number
            price = float(price)
            price_item.price = price 

    except:
        return price_item

    return price_item


        