import unicodedata

from requests import request
from bs4 import BeautifulSoup
from lxml import etree


class CianParser:
    def __init__(self, proxy_string):
        self.proxy_string = proxy_string
        self.dom = None
        self.fields_to_parse = {
            'price': '//*[@id="frontend-offer-card"]/div[2]/div[3]/div/div[1]/div[1]/div[1]/div[3]/div/div[1]/span',
            'total_meters': '//*[@id="frontend-offer-card"]/div[2]/div[2]/div[4]/div[1]/div[2]/span[2]',
            'min_metro': '//*[@id="frontend-offer-card"]/div[2]/div[2]/section/div/div/div[2]/address/ul[1]/li[1]/span',
            'address_string': '//*[@id="frontend-offer-card"]/div[2]/div[2]/section/div/div/div[2]/span'
        }

    def get_field_by_xpath(self, xpath):
        obj = self.dom.xpath(xpath)
        if not obj:
            return None

        if not obj[0].text:
            return obj[0].attrib['content']
        return obj[0].text.encode('ascii', errors='ignore').decode("utf-8")

    def parse_block(self, block):
        ru_name = block[0]
        interior_category = {'Дизайнерский': 'designer', 'Косметический': 'cosmetic', 'Без ремонта': 'no', 'Евроремонт': 'euro'}
        re_type_category = {'Вторичка': 'secondary', 'Новостройка': 'new'}
        type_of_house_category = {'Монолитный': 'monolithic', 'Панельный': 'panel', 'Кирпичный': 'brick', 'Деревянный': 'wooden', 'Блочный': 'block', 'Монолитно-кирпичный': 'brick_monolithic', 'Кирпично-монолитный': 'brick_monolithic', 'Сталинский': 'stalinist'}
        view = {'Во двор': 'into_the_yard', 'На улицу': 'in_the_street'}
        if ru_name == 'Жилая площадь':
            return {'living_meters': block[1].split()[0]}
        if ru_name == 'Площадь кухни':
            return {'kitchen_meters': block[1].split()[0]}
        if ru_name == 'Этаж':
            return {'floor_current': block[1].split()[0],
                    'floor_total': block[1].split()[2]}
        if ru_name == 'Год постройки':
            return {'year_built': block[1].split()[0]}
        if ru_name == 'Балкон/лоджия':
            return {'balcony': block[1].split()[0]}
        if ru_name == 'Ремонт':
            return {'interior': interior_category[block[1]]}
        if ru_name == 'Количество лифтов':
            return {'elevator_count': block[1].split()[0]}
        if ru_name == 'Парковка':
            return {'parking': 1}
        if ru_name == 'Тип жилья':
            return {'re_type': re_type_category[block[1].split()[0]]}
        if ru_name == 'Общая площадь':
            return {'total_meters': block[1].split()[0]}
        if ru_name == 'Тип дома':
            return {'type_of_house': type_of_house_category[block[1].split()[0]]}
        if ru_name == 'Вид из окна':
            return {'view': view[block[1].split()[0]]}
        return {}

    def parse_data_in_blocks(self, data_name):
        fractoids = self.dom.xpath(
            f'.//div[contains(concat(" ", normalize-space(@data-name), " "), " {data_name}")]')
        if not fractoids:
            return None

        blocks = []
        if data_name == 'ObjectFactoidsItem':
            for el in fractoids:
                blocks.append([unicodedata.normalize("NFKD", x) for x in (el[1][0].text, el[1][1].text)])
        else:
            for el in fractoids:
                blocks.append((el[0].text, el[1].text))

        blocks_data = {}
        for block in blocks:
            blocks_data.update(self.parse_block(block))
        return blocks_data

    def parse_object(self, url):
        req = request("GET", url)
        self.dom = etree.HTML(req.text)
        parsed_data = {}
        for field in self.fields_to_parse:
            parsed_data[field] = self.get_field_by_xpath(self.fields_to_parse[field])

        parsed_data.update(self.parse_data_in_blocks('ObjectFactoidsItem'))
        parsed_data.update(self.parse_data_in_blocks('OfferSummaryInfoItem'))
        return parsed_data

    def extract_links_from_page(self, page_url):
        req = request("GET", page_url)
        soup = BeautifulSoup(req.text, "html.parser")
        link_areas = soup.find_all("div", class_="_93444fe79c--content--lXy9G")
        links_sum = []
        for link_area in link_areas:
            link = link_area.find("a")
            if link:
                href = link.get("href")
                links_sum.append(href)

        next_page_link = soup.find("a", class_="_93444fe79c--button--Cp1dl _93444fe79c--link-button--Pewgf _93444fe79c--M--T3GjF _93444fe79c--button--dh5GL", string="Дальше")
        has_next_page = next_page_link is not None
        return links_sum, has_next_page

    def get_all_ad_data(self, start_url):
        page = 1
        while True:
            page_url = f"{start_url}&p={page}"
            ad_links, has_next_page = self.extract_links_from_page(page_url)
            for ad_link in ad_links:
                try:
                    ad_data = self.parse_object(ad_link)
                    print(ad_data)
                except Exception as e:
                    print(f"Error parsing {ad_link}: {e}")

                # Добавляем небольшую задержку перед следующим запросом
                # time.sleep(1)

            if not has_next_page:
                break
            page += 1


parser = CianParser("")
# print(parser.parse_object("https://www.cian.ru/sale/flat/291296532/"))
start_url = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=1&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1"
parser.get_all_ad_data(start_url)
