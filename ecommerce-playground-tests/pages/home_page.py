from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class HomePage(BasePage):
    FEATURED_SECTION = (By.CSS_SELECTOR, "#content .product-layout, .product-thumb, .product-layout")
    PRODUCT_LINK = (By.CSS_SELECTOR, "#content .product-layout .caption a, .product-thumb a, .product-layout a")
    COOKIE_CLOSE = (By.CSS_SELECTOR, ".cc-btn, .cookie-accept, .cookie-close, .close-cookie, .agree")

    def open(self):
        self.visit("")
        self._dismiss_overlays()

    def _dismiss_overlays(self, timeout=3):
        # Wait for page load then try clicking common cookie/consent buttons
        try:
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        except Exception:
            pass
        for _ in range(2):
            try:
                btns = self.driver.find_elements(*self.COOKIE_CLOSE)
                if btns:
                    for b in btns:
                        try:
                            b.click()
                        except Exception:
                            pass
                    return
            except Exception:
                pass

    def has_featured_products(self, timeout=10):
        try:
            elems = self.finds(*self.FEATURED_SECTION, timeout=timeout)
            if not elems:
                elems = self.finds(*self.PRODUCT_LINK, timeout=timeout)
            return len(elems) > 0
        except Exception:
            return False
        