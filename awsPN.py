import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re

driver = webdriver.Chrome()
driver.get("https://partners.amazonaws.com/search/partners/?loc=Manila&loctype=Headquarters&offeringType=Consulting%20Service%20%7C%20Managed%20Service%20%7C%20Professional%20Service%20%7C%20Value-Added%20Resale%20AWS%20Service")
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
print(driver.find_elements(By.CLASS_NAME,"tab-content-border"))
##print(driver.find_elements(By.XPATH,"//span[@class='psf-partner-search-details-card__title']"))
##print(soup.find_all("div",attrs={"id":"app"}))
##items = soup.find_all("div", attrs={"class":re.compile("^searchResults-container")})
##print(items)
##print(items[0].find("div", attrs={"class":"psf-partner-search-details-card__title"}).get_text)