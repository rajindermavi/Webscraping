
from selenium import webdriver
import validators 
import time
import requests
from bs4 import BeautifulSoup, element
import json
import pandas as pd      
import numpy as np
from usp.tree import sitemap_tree_for_homepage as sth

def get_pagelist_sth(url):
    tree = sth(url)
    page_list = list(set(page.url for page in tree.all_pages()))
    return page_list

def get_pagelist_bs(url):
    page_list = []
    try: 
        r = requests.get(url)
    except:
        print('Fail at', url)
        return page_list
    soup = BeautifulSoup(r.text,'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href[:4] != 'http':
            if href[0] == '/':
                page_list.append(url+href)
            else:
                page_list.append(url+'/'+href)
    
    return page_list


def get_pagelist(url):

    if url[:4] != 'http':
        url = 'https://' + url

    # First Attempt
    page_list = get_pagelist_sth(url)
    # Second Attempt
    if len(page_list) == 0:
        page_list = get_pagelist_bs(url)
    # Final
    if len(page_list) == 0:
        page_list = [url]

    page_list.sort(key = len)
        
    return page_list
    
def get_chromedriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222") 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1080x720")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_builtwith(driver, page_list):
    base_url = "https://builtwith.com" 
    sitewide_techs = {}

    for page in page_list:
        driver.get(base_url)
        element = driver.find_element_by_name("q")
        element.send_keys(page)
        driver.find_element_by_class_name("btn-primary").click()
        time.sleep(30)
        driver.implicitly_wait(10)
        current_url = driver.current_url
        
        res = requests.get(current_url)
        soup = BeautifulSoup(res.content, "html.parser")
        cards = soup.findAll("div", {"class": "card-body pb-0"})
        
        
        for card in cards:
            card_title = card.findAll("h6", {"class": "card-title"})[0].text
            if card_title not in sitewide_techs:
                sitewide_techs[card_title] = []

            card_attributes = card.findAll("a", {"class": "text-dark"})
            for attribute in card_attributes:
                if attribute not in sitewide_techs[card_title]:
                    sitewide_techs[card_title].append(attribute.text) 
             
    return sitewide_techs

def json_list_to_table(json_list):
    df_records = pd.DataFrame(json_list)
    df_records["count"] = 1

    table = pd.pivot_table(df_records, values = "count", index = "tech", columns = "url",aggfunc=np.sum)
    table.fillna(0,inplace = True)

    return table


if __name__ == "__main__":

    NCsurvey_df = pd.read_csv('NCsurvey.csv')
    url_list = list(filter(lambda x: x==x, NCsurvey_df.iloc[2,2:].values))[:3]  

    sitemaps = {}
    for url in url_list:
        sitemaps[url] = get_pagelist(url)[:20]

    with open('sitemaps.json', 'w') as file:
        json.dump(sitemaps,file)

    driver = get_chromedriver()

    survey_techs = {} 
    for url, pagelist in sitemaps.items():
        survey_techs[url] = scrape_builtwith(driver, pagelist)

    with open('survey_techs.json', 'w') as f:
        json.dump(survey_techs, f)
