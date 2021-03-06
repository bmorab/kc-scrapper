import os

import requests
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from blog_spider_teneder import BlogSpider

LAT_LNG_URL = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}"


def print_results_to_file(item, filep):
    print(
        f"{item.get('title')};{item.get('type')};{item.get('rating')};{item.get('reviews')};{item.get('address')};{item.get('latitude')};{item.get('longitude')};{item.get('postal_code')};{item.get('price')};{item.get('description')};{item.get('tags')};",
        file=filep)


def export_results(results):
    # Podeis cambiar la extension y el nombre del fichero el_tenedor.txt
    file_name = f"el-tenedor.csv"
    filep = open('./{}'.format(file_name), 'w')
    print(
        "TITLE;TYPE;RATING;REVIEWS;ADDRESS;LATITUDE;LONGITUDE;POSTAL_CODE;PRICE;DESCRIPTION;TAGS;",
        file=filep)
    [print_results_to_file(it, filep) for it in results]
    filep.close()


def get_lat_lng(item):
    res = requests.get(LAT_LNG_URL.format(item['address'], os.getenv('API_KEY')))
    results = res.json().get('results')[0]
    postal_code = [it.get('long_name') for it in results.get('address_components') if 'postal_code' in it.get('types')][
        0]
    location = results.get('geometry').get('location')
    item['latitude'] = location.get('lat', 0)
    item['longitude'] = location.get('lng', 0)
    item['postal_code'] = postal_code


def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_passed)

    process.crawl(BlogSpider)
    process.start()

    # ver cuales tienen 0 en lat lng y postal_code
    for item in results:
        get_lat_lng(item)

    export_results(results)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
