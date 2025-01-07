from io import BytesIO
import re
from kleinanzeigen_client import KleinanzeigenClient



class KleinanzeigenItem:

    def __init__(self, article) -> None:
        self.title = article.get('title', {}).get('value', '')
        self.url = next((item['href'] for item in article['link'] if item.get('rel') == 'self-public-website'), None)
        self.price = article.get('price', {}).get('amount', {}).get('value', '')
        self.urrency = article.get('price', {}).get('currency-iso-code', {}).get('value', {}).get('value', '')
        self.id = article.get('id', 0)
        self.state = article.get('ad-address', {}).get('state', {}).get('value', '')
        self.zip_code = article.get('ad-address', {}).get('zip-code', {}).get('value', '')
        self.location = '{} {}'.format(self.zip_code,self.state)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, KleinanzeigenItem) and self.url == __value.url

    def __str__(self) -> str:
        out_str = self.url + "\n"
        out_str += self.title + "\n"
        out_str += str(self.price) + " - "
        out_str += self.location
        return out_str

    def __hash__(self) -> int:
        return hash(self.id)

    def check_filters(self, filters):
        for pattern in filters:
            # Use re.search with IGNORECASE flag to check if the pattern matches self.url case-insensitively
            if re.search(pattern, self.url, re.IGNORECASE):
                return False  # Return False if a match is found

        return True


class KleinanzeigenBot:
    """
    Bot that querries a specified link and returns new articles if found
    """

    def __init__(self, url: str, name: str, api: KleinanzeigenClient) -> None:
        self.name = name
        self.url = url
        self.api = api

        data = api.get_ads(self.url)

        self.mainSet = set()

        for article in data:
            # self.mainSet.add(article.a['href'])
            self.mainSet.add(KleinanzeigenItem(article))

        self.invalid_link_flag = len(self.mainSet) <= 0

    def get_new_articles(self) -> set[KleinanzeigenItem]:
        data =  self.api.get_ads(self.url)

        newSet = set()
        for article in data:
            # newSet.add(article.a['href'])
            newSet.add(KleinanzeigenItem(article))

        newArticles = newSet.difference(self.mainSet)
        self.mainSet = self.mainSet.union(newArticles)

        return newArticles


    def show_articles(self) -> None:
        for item in self.mainSet:
            print(item)

    def num_items(self):
        return len(self.mainSet)


