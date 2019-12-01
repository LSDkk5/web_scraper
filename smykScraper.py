import json
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
        self.__get_products()
        
        
    def __get_request_content(self):
        return requests.get(self.__url, headers=self.__headers).content

    @staticmethod
    def __get_product_image(product_url, headers):
        image_raw = str(BeautifulSoup(requests.get(product_url, headers=headers).content, "html.parser").find_all('meta', itemprop='image'))
        return image_raw.split('"')[1] if image_raw else 'Error'

    def __get_products(self):
        for product in self.__soup.findAll('div', {'class': 'complex-product'}, limit=3):
            product_url = 'https://www.smyk.com'+product.find('a')['href']
            self.products.append(dict(product={
                'product_image': self.__get_product_image(product_url, self.__headers),
                'product_url': product_url,
                'product_description': product.find('div', {'class': 'complex-product__info'}).find("div", {'class': "complex-product__name"}).text,
                'product_price': product.find('div', {'class': 'complex-product__rating-price'}).find('div', {'class':"complex-product__price"}).find("span", {"class":"price--new"}).text
            }))
    
    def products_to_json(self):
        with open('products.json', 'w') as file: json.dump(self.products, file)

print(smykScraper('https://www.smyk.com/gry-planszowe/familijne.html').products)