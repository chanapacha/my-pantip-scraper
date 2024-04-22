from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

class PantipScraper:
    def __init__(self, scroll_iterations=0):
        self.scroll_iterations = scroll_iterations

    # Initialize the Chrome webdriver with specified options
    def web_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--verbose")
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920, 1200")
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)

    # Function to get URLs of topics based on tag list
    def get_topic_urls(self, tag_list):
        url_pre = 'https://pantip.com/tag/'
        urls = []

        # Initialize the Chrome driver
        driver = self.web_driver()
        try:
            for tag in tag_list:
                url_tag = url_pre + tag
                driver.get(url_tag)

                # Scroll the page down to load more topics if specified
                for _ in range(self.scroll_iterations):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for the page to load after scrolling

                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Find all topic links and append them to the list of URLs
                for topic in soup.find_all('li', {'class': 'pt-list-item'}):
                    link = topic.find('a')['href']
                    if link not in urls:
                        urls.append(link)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()  # Close the Selenium webdriver

        return urls

    # Function to scrape data (title and story) from each topic URL
    def scrape_topic_data(self, urls):
        data = []
        for u in urls:
            try:
                req = requests.get(u)
                bs = BeautifulSoup(req.content, 'html.parser')

                # Find title and story elements and extract text
                for k in bs.find_all('div', {'class': 'display-post-status-leftside'}):
                    topic_element = k.find('h2', {'class': 'display-post-title'})
                    if topic_element:
                        topic = topic_element.text.strip().replace('\n', '').replace('\t', '').replace('\xa0', '').replace('*', '').replace('\u200b', '')

                        story = bs.find('div', {'class': 'display-post-story'})
                        if story:
                            story_text = story.text.strip().replace('\n', '').replace('\t', '').replace('\xa0', '').replace('*', '').replace('\u200b', '')

                            # Append the data as a dictionary to the list
                            data.append({'url': u, 'title': topic, 'story': story_text})
            except Exception as e:
                print(f"An error occurred while scraping data from URL '{u}': {e}")

        return data

    # Function to convert scraped data to DataFrame
    def to_dataframe(self, data):
        return pd.DataFrame(data)
