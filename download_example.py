import requests
from xml.etree import ElementTree as ET

from requests.auth import HTTPBasicAuth


def get_orders_example():
    url = "https://tvoy.kz/commerceml?type=sale&mode=query"
    auth = HTTPBasicAuth('vendor@example.com', 'test12345')

    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(response.text)
        return
    with open('feed.xml', 'wb') as file:
        file.write(response.content)

