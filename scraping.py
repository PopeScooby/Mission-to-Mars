#!/usr/bin/env python
# coding: utf-8


# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(), 
        "hemispheres": mars_hems(browser)
    }
    
    browser.quit()
    return data

    if __name__ == "__main__":
        # If running as script, print scraped data
        print(scrape_all())


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def mars_hems(browser):

    url = 'https://marshemispheres.com/'

    browser.visit(url)
    #Create a list to hold the images and titles.
    hemisphere_image_urls = []

    #Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    all_hems_html = soup(html, 'html.parser')
    for x in all_hems_html.find_all("div", class_="item"):
        hemi_dict = {}
        
        #Get Image Page URL; Go There; Get the High Res Image URL
        img_page_url = url + x.find("a", class_="itemLink").get('href')
        browser.visit(img_page_url)
        html_b = browser.html
        img_page_html = soup(html_b, 'html.parser')
        hemi_dict["img_url"] = url + img_page_html.find("div", class_="downloads").find("li").find("a").get("href")
        
        #Get The Title
        hemi_dict["title"] = x.find("h3").text
        
        #Add Dictionary to link
        hemisphere_image_urls.append(hemi_dict)

    #return to the starting page
    browser.visit(url)
    return hemisphere_image_urls