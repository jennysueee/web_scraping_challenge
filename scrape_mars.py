from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import pandas as pd
import requests


def scrape():

    browser = Browser("chrome", executable_path="chromedriver", headless=False)
    news_title, news_paragraph = mars_news(browser)

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "weather": mars_weather(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
    }

    browser.quit()
    return data


def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    try:
        slide_element = soup.select_one("ul.item_list li.slide")
        slide_element.find("div", class_="content_title")
        news_title = slide_element.find("div", class_="content_title").get_text()
        news_paragraph = slide_element.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_paragraph


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()

    browser.is_element_present_by_text("more info", wait_time=1)
    more_info_element = browser.find_link_by_partial_text("more info")
    more_info_element.click()

    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    try:
        img_url = img_soup.select_one("figure.lede a img").get("src")

    except AttributeError:
        return None

    img_url = f"https://www.jpl.nasa.gov{img_url}"

    return img_url

def mars_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")

    tweet_attrs = {"class": "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text", "data-name": "Mars Weather"}
    mars_weather_tweet = weather_soup.find("div", attrs=tweet_attrs)
    mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    return mars_weather


def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["Description", "Value"]
    df.set_index("Description", inplace=True)

    return df.to_html(classes="table table-striped")


def hemispheres(browser):

    url = ("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
    browser.visit(url)

    links = browser.find_by_css("a.product-item h3")
    for item in range(len(links)):
        hemisphere = {}
        browser.find_by_css("a.product-item h3")[item].click()
        sample_element = browser.find_link_by_text("Sample").first
        hemisphere["img_url"] = sample_element["href"]
        hemisphere["title"] = browser.find_by_css("h2.title").text
        
        hemisphere_image_urls.append(hemisphere)
        
        browser.back()

        return hemisphere_image_urls

def scrape_hemisphere(html_text):

    hemi_soup = BeautifulSoup(html_text, "html.parser")

    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:
        title_elem = None
        sample_elem = None

    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemisphere


if __name__ == "__main__":

    print(scrape())
