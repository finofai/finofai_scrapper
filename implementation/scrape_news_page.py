from typing import Optional, Dict
import time, json
from html import unescape
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from implementation.selenium_driver import get_driver


async def scrape_bs_article(url: str) -> Dict[str, Optional[str]]:


    driver = await get_driver()
    try:
        driver.get(url)

        # 2) Dismiss the topic-select popup if it appears
        try:
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Cancel']"))
            ).click()
        except TimeoutException:
            pass

        # 3) Give any JS a moment to load the JSON-LD
        time.sleep(2)

        # 4) Grab title & author & datePublished from the rendered DOM
        title = driver.find_element(By.TAG_NAME, "h1").text
        try:
            author = driver.find_element(By.CSS_SELECTOR, "span.font-bold").text
        except:
            author = None

        # 5) Find all JSON-LD blocks and parse out the NewsArticle one
        body = None
        date_published = None
        scripts = driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
        for s in scripts:
            raw = s.get_attribute("innerText")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            # JSON-LD may be a list or single object
            entries = data if isinstance(data, list) else [data]
            for entry in entries:
                if entry.get("@type") == "NewsArticle" and "articleBody" in entry:
                    # pull out the plain-text body and date
                    body = unescape(entry["articleBody"])
                    date_published = entry.get("datePublished") or entry.get("dateModified")
                    break
            if body:
                break

    finally:
        driver.quit()

    return {
        "url":   url,
        "title": title,
        "author": author,
        "date":  date_published,
        "body":  body
    }

