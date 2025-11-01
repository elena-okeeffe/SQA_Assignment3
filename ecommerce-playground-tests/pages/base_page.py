# pages/base_page.py
import time
import os
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import urljoin

class BasePage:
    DEFAULT_TIMEOUT = 10
    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def visit(self, path: str = ""):
        if path is None:
            path = ""
        if not isinstance(path, str):
            # convert tuples/lists/dicts to string so driver.get doesn't receive non-string
            path = str(path)
        url = urljoin(self.base_url, path)
        # debug guard
        if not isinstance(url, str):
            raise TypeError(f"Constructed url must be a string, got {type(url).__name__}")
        self.driver.get(url)

    def find(self, by, value, timeout=None):
        w = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return w.until(EC.presence_of_element_located((by, value)))

    def finds(self, by, value, timeout=None):
        w = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return w.until(lambda d: d.find_elements(by, value))

    def title(self):
        return self.driver.title
    
    def take_screenshot(self, name: str = None):
        """
        Take a screenshot and save it to a screenshots directory.
        If name is provided, use it; otherwise generate a timestamp-based name.
        Returns the full path to the saved screenshot.
        """
        # Create screenshots directory if it doesn't exist
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate filename
        if name:
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        else:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(screenshots_dir, filename)
        self.driver.save_screenshot(filepath)
        print(f"SCREENSHOT SAVED: {filepath}")
        return filepath
    
    def wait_for_page_ready(self, timeout: int = None):
        to = timeout or self.DEFAULT_TIMEOUT
        wait = WebDriverWait(self.driver, to)
        try:
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        except Exception:
            pass
        # small additional pause to allow client-side rendering
        time.sleep(0.2)



    def _dismiss_overlays(self, timeout=3):
        """
        Best-effort dismissal of cookie banners / overlays / modals that block interaction.
        This method intentionally swallows exceptions so callers can continue even if nothing was dismissed.
        """
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        except TimeoutException:
            pass

        candidates = [
            "button.cc-allow",
            ".cc-btn",
            ".cookie-accept",
            ".cookie-consent__accept",
            "button.cookie-accept",
            "button[aria-label='close']",
            "button[title*='Accept']",
            "button[title*='Close']",
            "a.cookie-accept",
            ".accept-cookies",
            ".agree",
            ".banner-close",
            ".close-cookie",
            "button#accept-cookies",
        ]

        try:
            for sel in candidates:
                try:
                    els = self.driver.find_elements("css selector", sel)
                except WebDriverException:
                    els = []
                if not els:
                    continue
                for el in els:
                    try:
                        el.click()
                    except Exception:
                        try:
                            self.driver.execute_script("arguments[0].click();", el)
                        except Exception:
                            pass
                # If we clicked something, give the page a short moment
                return
        except Exception:
            # swallow any unexpected exception to avoid breaking callers
            return

        # Final fallbacks
        try:
            fallbacks = ["[data-dismiss='modal']", "button.close", ".modal-close"]
            for sel in fallbacks:
                try:
                    els = self.driver.find_elements("css selector", sel)
                except WebDriverException:
                    els = []
                if not els:
                    continue
                for el in els:
                    try:
                        el.click()
                    except Exception:
                        try:
                            self.driver.execute_script("arguments[0].click();", el)
                        except Exception:
                            pass
                return
        except Exception:
            return