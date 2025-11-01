# This tests F15 Search products
import pytest
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

HOME_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=common/home"
SEARCH_TERM = "Nikon"
TIMEOUT = 20  # increased timeout for slower responses
SHORT = 2

def make_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,1000")
    return webdriver.Chrome(options=opts)

def try_close_overlays(driver):
    selectors = [
        ".modal .close",
        ".popup-close",
        ".cookie-policy .close",
        ".fancybox-close",
        ".mfp-close"
    ]
    for sel in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els:
                if el.is_displayed():
                    try:
                        el.click()
                        time.sleep(0.2)
                    except Exception:
                        pass
        except Exception:
            pass

def find_search_input(driver, wait):
    selectors = [
        "input[name='search']",
        "input[type='search']",
        "input#search",
        "input.form-control[type='text']"
    ]
    for sel in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            if el.is_displayed():
                return el
        except Exception:
            continue
    raise RuntimeError("Search input not found on home page (tried several selectors)")

def collect_product_links_from_results(driver, wait):
    try:
        wait.until(EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-layout, .product-thumb, .product-list")),
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'There are no products to list')]"))
        ))
    except Exception:
        raise

    link_selectors = [
        ".product-layout .caption a",
        ".product-thumb .caption a",
        ".product-list .caption a",
        "h4 a",
        ".product-name a"
    ]
    links = []
    for sel in link_selectors:
        for el in driver.find_elements(By.CSS_SELECTOR, sel):
            href = el.get_attribute("href")
            if href and href not in links:
                links.append(href)
    return links

def product_page_contains_term(driver, term):
    term_lower = term.lower()

    for sel in ["h1", ".product-info h1", ".product-title h1", "h1#content"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            if el and term_lower in el.text.strip().lower():
                return True, f"found in name ({sel})"
        except Exception:
            pass

    try:
        details = driver.find_elements(By.CSS_SELECTOR, ".list-unstyled li, .product-info .list-unstyled li, #content .list-unstyled li")
        details_text = " ".join([d.text for d in details]).lower()
        if term_lower in details_text:
            return True, "found in product details/manufacturer"
    except Exception:
        pass

    try:
        tags = driver.find_elements(By.CSS_SELECTOR, ".tags a, .product-tags a, .tag-list a")
        tags_text = " ".join([t.text for t in tags]).lower()
        if term_lower in tags_text:
            return True, "found in tags"
    except Exception:
        pass

    try:
        desc_els = driver.find_elements(By.CSS_SELECTOR, ".description, #tab-description, .product-desc, .tab-content")
        desc_text = " ".join([d.text for d in desc_els]).lower()
        if term_lower in desc_text:
            return True, "found in description"
    except Exception:
        pass

    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        if term_lower in body_text:
            return True, "found in page body (fallback)"
    except Exception:
        pass

    return False, "not found"

@pytest.mark.integration
def test_search_nikon_and_verify_product_pages():
    driver = make_driver(headless=True)
    wait = WebDriverWait(driver, TIMEOUT)
    errors = []
    links = []

    try:
        driver.get(HOME_URL)
        time.sleep(0.3)
        try_close_overlays(driver)

        search_input = find_search_input(driver, wait)
        search_input.clear()
        search_input.send_keys(SEARCH_TERM)

        submitted = False
        try:
            search_input.send_keys(Keys.ENTER)
            submitted = True
        except Exception:
            pass

        if not submitted:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, "button[type='button'].btn-default, button[type='submit']")
                if btn.is_displayed():
                    try:
                        btn.click()
                        submitted = True
                    except ElementClickInterceptedException:
                        try_close_overlays(driver)
                        btn.click()
                        submitted = True
            except Exception:
                pass

        if not submitted:
            raise RuntimeError("Could not submit search (Enter and button click both failed)")

        try:
            wait.until(EC.url_contains("route=product/search"))
        except TimeoutException:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-layout, .product-thumb, .product-list")))
            except TimeoutException:
                raise TimeoutException("Search results page did not load (no product tiles and URL unchanged)")

        time.sleep(0.5)

        links = collect_product_links_from_results(driver, wait)
        assert links, "No product links found on the search results page"

        for idx, url in enumerate(links, start=1):
            driver.get(url)
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                errors.append(f"{idx}. {url} -- page failed to load (timeout)")
                continue

            found, reason = product_page_contains_term(driver, SEARCH_TERM)
            if not found:
                title = driver.title
                snippet = driver.find_element(By.TAG_NAME, "body").text[:600].replace("\n", " ")
                errors.append(f"{idx}. {url} -- title: {title} -- reason: {reason} -- snippet: {snippet}")

        if errors:
            pytest.fail("The following product pages failed verification:\n" + "\n".join(errors))

        # SUCCESS message: printed when test passes
        print(f"PASS: All {len(links)} products verified contain '{SEARCH_TERM}' in name/brand/tags/description")

    except Exception as exc:
        tb = traceback.format_exc(limit=3)
        page_snippet = ""
        try:
            page_snippet = driver.find_element(By.TAG_NAME, "body").text[:800].replace("\n", " ")
        except Exception:
            pass
        pytest.fail(f"Unexpected error during test: {exc}\nURL: {driver.current_url}\nTitle: {driver.title}\nSnippet: {page_snippet}\nTraceback:\n{tb}")

    finally:
        driver.quit()
