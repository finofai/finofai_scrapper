#!/usr/bin/env python3
"""
bs_selenium_scraper_uc.py

• Uses Selenium WebDriver to open RSS feed URLs
• Renders each RSS URL in headless Chrome
• Extracts raw XML from the <pre> tag
• Parses via feedparser, yields minimal records
"""
import asyncio
import hashlib
import time
import calendar
import feedparser
import pendulum
from pendulum.parsing.exceptions import ParserError
from qdrant_client.http.exceptions import UnexpectedResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from webdriver_manager.chrome import ChromeDriverManager
from implementation.selenium_driver import get_driver
from pprint import pprint
from implementation.scrape_news_page import scrape_bs_article
from implementation.embed import embed_article
from multiprocessing import Process,cpu_count,Pool
from implementation.insert_points import insert_points
import uuid

# RSS feed URLs
FEEDS = {
    # ── original ───────────────────────────────────────────────
    "markets":      "https://www.business-standard.com/rss/markets-106.rss",
    "auto":         "https://www.business-standard.com/rss/industry/auto-21701.rss",
    "finance":      "https://www.business-standard.com/rss/finance-103.rss",
    "economy":      "https://www.business-standard.com/rss/economy-104.rss",
    "companies":    "https://www.business-standard.com/rss/companies-101.rss",
    "banking":      "https://www.business-standard.com/rss/industry/banking-21703.rss",
    "commodities":  "https://www.business-standard.com/rss/markets/commodities-10608.rss",
    "ipo":          "https://www.business-standard.com/rss/markets/ipo-107.rss",

    # ── extra market-moving sub-feeds ──────────────────────────
    "stock_market_news":  "https://www.business-standard.com/rss/markets/stock-market-news-10618.rss",
    "markets_news":       "https://www.business-standard.com/rss/markets/news-10601.rss",
    "markets_interviews": "https://www.business-standard.com/rss/markets/interviews-10624.rss",
    "crypto":             "https://www.business-standard.com/rss/markets/cryptocurrency-10622.rss",

    # ── industry verticals ────────────────────────────────────
    "sme":          "https://www.business-standard.com/rss/industry/sme-21702.rss",
    "agriculture":  "https://www.business-standard.com/rss/industry/agriculture-21704.rss",
    "aviation":     "https://www.business-standard.com/rss/industry/aviation-21706.rss",

    # ── tech & innovation ─────────────────────────────────────
    "technology":   "https://www.business-standard.com/rss/technology-108.rss",
    "tech_news":    "https://www.business-standard.com/rss/technology/tech-news-10817.rss",
    "gadgets":      "https://www.business-standard.com/rss/technology/gadgets-10819.rss",

    # ── healthcare & pharma ───────────────────────────────────
    "health":       "https://www.business-standard.com/rss/health-185.rss",

    # ── company-focused streams ───────────────────────────────
    "companies_news":       "https://www.business-standard.com/rss/companies/news-10101.rss",
    "companies_people":     "https://www.business-standard.com/rss/companies/people-10121.rss",
    "companies_quarterly":  "https://www.business-standard.com/rss/companies/quarterly-results-10103.rss",
    "companies_interviews": "https://www.business-standard.com/rss/companies/interviews-10122.rss",
    "companies_startups":   "https://www.business-standard.com/rss/companies/start-ups-10113.rss",
}


from hashlib import sha256

def get_point_id_from_url(url: str) -> str:
    return sha256(url.encode()).hexdigest()


def get_deterministic_uuid_from_url(url: str) -> str:
    sha_hash = hashlib.sha256(url.encode()).digest()  # 32 bytes
    return str(uuid.UUID(bytes=sha_hash[:16]))




async def fetch_xml(driver, url):
    """
    Load the RSS URL and extract raw XML.
    Tries to fetch from <pre>; if unavailable, falls back to <body> text.
    """
    driver.get(url)
    try:
        pre = driver.find_element(By.TAG_NAME, "pre")
        return pre.text
    except Exception:
        return driver.find_element(By.TAG_NAME, "body").text


async def parse_feed(driver, sector, url):
    time.sleep(1)
    xml =await  fetch_xml(driver, url)
    #print(xml)
    parsed = feedparser.parse(xml)
    for entry in parsed.entries:
        uid = hashlib.md5(entry.link.encode()).hexdigest()
        # Parse publication time, fallback to published_parsed if needed
        try:
            ts = pendulum.parse(entry.published).to_iso8601_string()
        except (ParserError, TypeError):
            # Use published_parsed struct_time
            struct = entry.get('published_parsed') or entry.get('updated_parsed')
            if struct:
                timestamp = calendar.timegm(struct)
                ts = pendulum.from_timestamp(timestamp).to_iso8601_string()
            else:
                ts = pendulum.now().to_iso8601_string()
        # Continue building record
        yield {
            "id":      uid,
            "ts":      ts,
            "sector":  sector,
            "title":   entry.title,
            "snippet": entry.summary[:200],
            "url":     entry.link,
        }





async def sector_scrape(sector,url):
    count = 0
    driver =  await get_driver()
    async for rec in parse_feed(driver, sector, url):

        pprint(rec, indent=3, width=150)
        count += 1
        article = await scrape_bs_article(rec['url'])

        article_id = get_deterministic_uuid_from_url(rec['url'])
        headline = article['title']
        body = article['body']
        embeded_points = await embed_article(article_id, headline, body,rec['url'])
        await insert_points(embeded_points)
        print("---------points inserted---")


    driver.quit()



def sync_sector_scrape(sector,url):
    try:
        asyncio.run(sector_scrape(sector, url))
    except UnexpectedResponse as e:
        # handle/log it here; don’t let it bubble out
        print(f"[{sector}] got bad response: {e!r}")
    except Exception:
        # other errors
        import traceback;
        traceback.print_exc()


def main():

    num_workers = min(4, cpu_count())

    with Pool(processes=num_workers) as pool:
        pool.starmap(sync_sector_scrape, FEEDS.items())
    #driver.quit()
if __name__=='__main__':
    main()

