
from selenium import webdriver
import validators 
import time
import requests
from bs4 import BeautifulSoup, element
import json
import pandas as pd      
import numpy as np


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222") 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1080x720")
    driver = webdriver.Chrome(options=options)
    return driver

def get_sitemap(driver, url):

    sitemapper = 'https://xml-sitemaps.com'
    driver.get(sitemapper)
    element = driver.find_element_by_name("initurl")
    element.send_keys(url)
    driver.find_element_by_class_name("btn-block").click()

    time.sleep(600)

    driver.find_element_by_class_name("view_details").click()
 
    current_url = driver.current_url
    res = requests.get(current_url)

    soup = BeautifulSoup(res.content, "html.parser")
    long_list = soup.findAll("div", {"class": "long-list"})

    sites = long_list[0].findAll("td")
    site_list = []

    for site in sites:
        if site.text[:5] == "https":
            site_list.append(site.text)
        
    return site_list


def scrape_builtwith(driver, base_url, url_list):
    driver.get(base_url)
    survey_tech_list = []

    for url in url_list:
        element = driver.find_element_by_name("q")
        element.send_keys(url)
        driver.find_element_by_class_name("btn-primary").click()
        time.sleep(30)
        driver.implicitly_wait(10)
        current_url = driver.current_url
        #current_url = base_url + '/' + url
        
        res = requests.get(current_url)
        soup = BeautifulSoup(res.content, "html.parser")
        divs = soup.findAll("div", {"class": "row mb-2 mt-2"})

        for div in divs:
            elt = div.findAll("a")[0]
            survey_tech_list.append({'url': url, 'tech': elt.text ,'href': elt.attrs["href"] })

    return survey_tech_list

def json_list_to_table(json_list):
    df_records = pd.DataFrame(json_list)
    df_records["count"] = 1

    table = pd.pivot_table(df_records, values = "count", index = "tech", columns = "url",aggfunc=np.sum)
    table.fillna(0,inplace = True)

    return table


if __name__ == "__main__":

    NCsurvey_df = pd.read_csv('NCsurvey.csv')
    url_list = list(filter(lambda x: x==x, NCsurvey_df.iloc[2,2:].values))  

    driver = get_driver()
    
    sitemaps = {}
    for url in url_list[:3]:
        sitemaps[url] = get_sitemap(driver,url)

    with open('sitemaps.json') as file:
        json.dump(sitemaps,file)
    
    #base_url = "https://builtwith.com"     

    #survey_tech_list = scrape_builtwith(driver, base_url, url_list)

    #with open('data.json', 'w') as f:
    #    json.dump(survey_tech_list, f)

    #table = json_list_to_table(survey_tech_list)

    #table.to_csv("tech_table.csv")