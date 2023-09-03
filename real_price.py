from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time
import csv
import json

# Загрузка словаря из JSON файла
with open('address_to_houseid.json', 'r', encoding='utf-8') as json_file:
    address_to_houseid = json.load(json_file)


chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
# chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)
class CianPriceParser():

    def get_data(self, address, rooms, total_meters):
        self.address = address
        self.rooms = rooms
        self.meters = total_meters

    def send_data(self):
        try:

            driver.get('https://www.cian.ru/kalkulator-nedvizhimosti/')

            address_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="geo-suggest-input"]')))
            address_input.send_keys(self.address)
            total_area_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="realty-valuation-frontend"]/div/div[1]/div[2]/div/div[1]/div[1]/form/div/div[4]/div/div/div/input')))
            total_area_input.send_keys(self.meters)

            rooms_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="realty-valuation-frontend"]/div/div[1]/div[2]/div/div[1]/div[1]/form/div/div[3]/div/div/button')))
            rooms_button.click()

            if self.rooms == '1':
                rooms_option = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/label[2]/span')))
                rooms_option.click()
            elif self.rooms == '2':
                rooms_option = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/label[3]/span')))
                rooms_option.click()
            elif self.rooms == '3':
                rooms_option = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/label[4]/span')))
                rooms_option.click()
            else:
                rooms_option = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/label[5]/span')))
                rooms_option.click()

            estimate_button = wait.until(EC.presence_of_element_located(
                (
                By.XPATH, '//*[@id="realty-valuation-frontend"]/div/div[1]/div[2]/div/div[2]/div/div/button/span')))
            estimate_button.click()
        except:
            driver.quit()


    def skip_pages(self):

        try:
            # Нажатие "нет, не агент по недвижмости"
            wait.until(EC.presence_of_element_located((By.XPATH,
                                                            '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[2]/div/div[2]/div[2]')))
            driver.find_element(By.XPATH,
                                     '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[2]/div/div[2]/div[2]').click()

            # Нажатие "Просто интересно"
            wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[2]/div/div[6]/div[1]/span')))
            driver.find_element(By.XPATH,
                                     '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[2]/div/div[6]/div[1]/span').click()

            # Нажатие "Нет, спасибо"
            wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[3]/div/div/div[2]/button[2]/span')))
            driver.find_element(By.XPATH,
                                     '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[3]/div/div/div[2]/button[2]/span').click()

            # Нажатие "Нет"
            wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[3]/div/div[2]/div[1]')))
            driver.find_element(By.XPATH,
                                     '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[3]/div/div[2]/div[1]').click()

            # Нажатие "Показать оценку"
            wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[3]/div[2]/button[1]/span')))
            driver.find_element(By.XPATH,
                                     '//*[@id="request-form-valuation-frontend"]/div/div/div/div[2]/div/div[2]/div[2]/form/div[3]/div[2]/button[1]/span').click()

            # Подождать, пока будет отображена оценка
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="estimation"]/div/div[2]/span[2]')))

            # Получение Средней оценки
            estimated_price_element = driver.find_element(By.CSS_SELECTOR,
                                                          "#estimation .f0b5faa8cb--text_letterSpacing__0--cQxU5")
            estimated_price = estimated_price_element.text

            return estimated_price
        finally:
            driver.quit()


    def parse_data(self, address, rooms, total_meters):
        try:
            self.get_data(address, rooms, total_meters)
            self.send_data()
            price = self.skip_pages()
            return price
        except Exception as e:
            print(e)
            return None



parser = CianPriceParser()
with open("price_parsing_data.csv", 'r', encoding='utf-8') as csvfile:
    flats_data = csv.reader(csvfile)
    for row in flats_data:
        address = row[1]
        rooms = row[2]
        total_area = row[3].split(',')[0]
        print(parser.parse_data(address, rooms, total_area))
