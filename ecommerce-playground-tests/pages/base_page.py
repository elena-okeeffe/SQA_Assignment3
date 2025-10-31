# pages/base_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class BasePage:
    def __init__(self, driver, base_url=None, wait=10):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, wait)

    def visit(self, path=""):
        url = self.base_url if not path else f"{self.base_url}{path}"
        self.driver.get(url)

    def find(self, by, value, timeout=None):
        w = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return w.until(EC.presence_of_element_located((by, value)))

    def finds(self, by, value, timeout=None):
        w = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return w.until(lambda d: d.find_elements(by, value))

    def title(self):
        return self.driver.title

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