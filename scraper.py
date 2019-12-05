import json
import time
import asyncio
import schedule
import requests
import motor.motor_asyncio
from bs4 import BeautifulSoup

dbUrl = 'mongodb+srv://'

class smykScraper(object):
    def __init__(self, url):
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko)',
        }
        self.__url = url

        self.__soup = BeautifulSoup(self.__get_request_content(), "html.parser")

        loop = asyncio.new_event_loop()
        self.client = motor.motor_asyncio.AsyncIOMotorClient(dbUrl, io_loop=loop)
        loop.run_until_complete(self.__get_products())
        loop.close()

    def __get_request_content(self):
        return requests.get(self.__url, headers=self.__headers).content

    @staticmethod
    async def __get_product_image(product_url, headers):
        image_raw = str(BeautifulSoup(requests.get(product_url, headers=headers).content, 
            "html.parser").find_all('meta', itemprop='image'))
        return image_raw.split('"')[1] if image_raw else None

    async def __get_products(self):
        for product in self.__soup.findAll('div', {'class': 'complex-product'}, limit=5):
            product_url = 'https://www.smyk.com'+product.find('a')['href']
            if 'ubrania-i-buty' in self.__url:
                product = dict({
                    'image': await self.__get_product_image(product_url, self.__headers),
                    'url': product_url,
                    'description':  await self.__get_description(product),
                    'price':  await self.__get_price(product),
                    'sizes': (await self.__get_clothes_details(product_url, self.__headers))[0],
                    'color': (await self.__get_clothes_details(product_url, self.__headers))[1],
                })
            else:
                product = dict({
                    'image': await self.__get_product_image(product_url, self.__headers),
                    'url': product_url,
                    'description':  await self.__get_description(product),
                    'price':  await self.__get_price(product),
                })
            await self.__insert_to_database(product)
    
    @staticmethod
    async def __get_description(product):
        return product.find('div', {'class': 'complex-product__info'}
            ).find("div", {'class': "complex-product__name"}).text

    @staticmethod
    async def __get_price(product):
        return product.find('div', {'class': 'complex-product__rating-price'}
            ).find('div', {'class':"complex-product__price"}
            ).find("span", {"class":"price--new"}).text

    @staticmethod
    async def __get_clothes_details(product_url, headers):
        page = BeautifulSoup(requests.get(product_url, headers=headers).content, "html.parser")
        return ([size.text for size in page.find_all('div', {'class': 'size__item'})],
             page.find('span', {'class': 'black'}).text)

    async def __insert_to_database(self, product):
        result = await self.client.test.user.insert_one(product)


urls = ['https://www.smyk.com/gry-planszowe/familijne.html', 
        'https://www.smyk.com/ubrania-i-buty/kolekcja-jesien-zima/dziewczynka-9-14.html']


for u in urls:
    smykScraper(u)
    # schedule.every().day.at('03:00').do()
    
# while True:
#     schedule.run_pending()
#     time.sleep(1)