from selenium.webdriver import Chrome
from selenium.webdriver.support.select import Select


class WebLinks:
    def __init__(self):
        webdriver = '/Users/RitaFigueiredo/Documents/chromedriver'
        driver = Chrome(webdriver)
        url = 'https://rightmove.co.uk'
        driver.get(url)
        neighbourhood = 'Islington'
        search = driver.find_element_by_id('searchLocation')
        search.send_keys(neighbourhood)
        rent_button = driver.find_element_by_id('rent')
        rent_button.click()
        select_location = Select(driver.find_element_by_id('locationIdentifier'))
        select_location.select_by_index(0)
        select_min_bedrooms = Select(driver.find_element_by_id('minBedrooms'))
        select_min_bedrooms.select_by_value('0')
        select_max_bedrooms = Select(driver.find_element_by_id('maxBedrooms'))
        select_max_bedrooms.select_by_value('1')
        select_added_to_site = Select(driver.find_element_by_id('maxDaysSinceAdded'))
        select_added_to_site.select_by_value('3')
        rent_button = driver.find_element_by_id('submit')
        rent_button.click()
        home_links = driver.find_elements_by_class_name('propertyCard-link')
        list_links = []
        for link in home_links:
            list_links.append(link.get_attribute('href'))

        self.list_urls = list_links

    def get_list(self):
        return self.list_urls



#homes_titles = driver.find_elements_by_class_name('propertyCard-title')
#homes_addresses = driver.find_elements_by_class_name('propertyCard-address')
# homes_prices = driver.find_elements_by_class_name('propertyCard-priceValue')
# titles = [x.text for x in homes_titles]
# addresses = [x.text for x in homes_addresses]
# prices = [x.text for x in homes_prices]
# print(titles)
# print(addresses)
# print(prices)
# print(len(titles))

