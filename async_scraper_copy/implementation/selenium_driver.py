from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ──────────────────────────────────────────────────────────────
#  Use the Selenium Grid that the base image has already started
# ──────────────────────────────────────────────────────────────
def get_driver() -> webdriver.Remote:
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )

    opts = Options()
    opts.add_argument("--headless=new")         # stay headless
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"--user-agent={USER_AGENT}")

    # Selenium server lives inside the SAME container on port 4444
    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4444/wd/hub",
        options=opts,
    )
    return driver
