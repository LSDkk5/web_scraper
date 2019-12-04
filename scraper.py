import json
import time
import asyncio
import schedule
import requests
from bs4 import BeautifulSoup


class smykScraper(object):
    def __init__(self, url):
        self.products = []

        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko)',
        }
        self.__url = url

        self.__soup = BeautifulSoup(self.__get_request_content(), "html.parser")

        loop = asyncio.new_event_loop()
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
        for product in self.__soup.findAll('div', {'class': 'complex-product'}):
            product_url = 'https://www.smyk.com'+product.find('a')['href']
            if 'ubrania-i-buty' in self.__url:
                self.products.append(dict({
                    'product_image': await self.__get_product_image(product_url, self.__headers),
                    'product_url': product_url,
                    'product_description':  await self.__get_description(product),
                    'product_price':  await self.__get_price(product),
                    'product_sizes': await self.__get_clothes_details(product_url, self.__headers)[0],
                    'product_color': await self.__get_clothes_details(product_url, self.__headers)[1],
                }))
            else:
                self.products.append(dict({
                    'product_image': await self.__get_product_image(product_url, self.__headers),
                    'product_url': product_url,
                    'product_description':  await self.__get_description(product),
                    'product_price':  await self.__get_price(product)
                }))                
    
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

    def json_result(self):
        with open('products.json', 'a+') as file: json.dump(self.products, 
            file, indent=4, sort_keys=True)


urls = ['https://www.smyk.com/gry-planszowe/familijne.html', 
        'https://www.smyk.com/ubrania-i-buty/kolekcja-jesien-zima/dziewczynka-9-14.html']


for u in urls:
    schedule.every().day.at('03:00').do(smykScraper(u).json_result)
    
while True:
    schedule.run_pending()
    time.sleep(1)