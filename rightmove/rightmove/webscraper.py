from selenium.webdriver import Chrome
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

DELAY = 15  # seconds
neighbourhoods = []

f = open('rightmove/data/london-areas.txt')
neighbourhood = f.readline()
neighbourhoods.append(neighbourhood.strip())
while neighbourhood:
    neighbourhood = f.readline()
    neighbourhoods.append(neighbourhood.strip())
f.close()

neighbourhoods.remove('')

class WebLinks:
    def __init__(self):
        self.list_urls = []

        for area in neighbourhoods:
            try:
                webdriver = '/Users/RitaFigueiredo/Documents/chromedriver'
                driver = Chrome(webdriver)
                url = 'https://rightmove.co.uk'
                driver.get(url)
                search = WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.ID, 'searchLocation')))
                search.send_keys(area)
                rent = driver.find_element_by_id('rent')
                rent.click()
                time.sleep(1)

                if driver.find_element_by_id('locationIdentifier').is_displayed():
                    select_location = Select(driver.find_element_by_id('locationIdentifier'))
                    select_location.select_by_index(0)


                select_min_bedrooms = Select(driver.find_element_by_id('minBedrooms'))
                select_min_bedrooms.select_by_value('0')
                select_max_bedrooms = Select(driver.find_element_by_id('maxBedrooms'))
                select_max_bedrooms.select_by_value('2')
                select_added_to_site = Select(driver.find_element_by_id('maxDaysSinceAdded'))
                select_added_to_site.select_by_value('1')
                rent = driver.find_element_by_id('submit')
                rent.click()

                time.sleep(2)

                home_links = driver.find_elements_by_class_name('propertyCard-link')

                for link in home_links:
                    self.list_urls.append(link.get_attribute('href'))

                time.sleep(2)
                while True:
                    next_button = driver.find_element_by_class_name(
                        'pagination-button.pagination-direction.pagination-direction--next')

                    if not next_button.is_enabled():
                        break
                    next_button.click()
                    time.sleep(3)
                    home_links = driver.find_elements_by_class_name('propertyCard-link')
                    for link in home_links:
                        self.list_urls.append(link.get_attribute('href'))
                    time.sleep(3)
            except TimeoutException:
                print("Loading took too much time!")
            time.sleep(2)

    def get_list(self):
        self.list_urls = list(set(self.list_urls))
        return self.list_urls


if __name__ == '__main__':
    list_w = WebLinks().get_list()
    print(list_w)
    print(len(list_w))

