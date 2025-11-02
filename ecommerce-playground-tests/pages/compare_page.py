# pages/compare_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage


class ComparePage(BasePage):
    COMPARE_TABLE = (By.CSS_SELECTOR, "#content table, .compare-product, .table-responsive table")
    COMPARE_ITEMS = (By.CSS_SELECTOR, "#content table tr, .compare-product, .table-responsive tbody tr")
    REMOVE_BUTTON = (
        By.CSS_SELECTOR,
        "a[href*='remove'], .btn-danger, .remove, td a[href*='remove'], "
        "input[value*='Remove'], button[value*='Remove']"
    )
    EMPTY_MESSAGE = (
        By.XPATH,
        "//*[@id='content']//p[contains(text(), 'not chosen') or contains(text(), 'no products')] | "
        "//*[contains(@class, 'alert-info')] | "
        "//*[contains(@class, 'empty')] | "
        "//*[@id='content']/p"
    )
    SUCCESS_MESSAGE = (
        By.CSS_SELECTOR,
        ".alert-success, .alert.alert-success, .alert-dismissible.alert-success, "
        "div.alert-success, .alert-success .close"
    )

    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)

    def open(self):
        """Opening the compare page directly"""
        self.visit("index.php?route=product/compare")
        self.wait_for_page_ready()
        self._dismiss_overlays()

    def open_from_main_header(self):
        """Navigating to compare page from main header"""
        self.visit("")
        self._dismiss_overlays()
        try:
            # Finding compare button in header 
            compare_locators = [
                (By.CSS_SELECTOR, "div#entry_217823 a[aria-label='Compare']"),
                (By.XPATH, "//div[@id='entry_217823']//a[@aria-label='Compare']"),
                (By.XPATH, "//header//div[@id='entry_217823']//a[contains(@href, 'product/compare')]"),
                (By.XPATH, "//header//a[@aria-label='Compare']"),
                (By.XPATH, "//header//a[contains(@href, 'product/compare')]"),
                (By.XPATH, "//a[@aria-label='Compare']"),   
                (By.XPATH, "//a[contains(@href, 'product/compare')]")
            ]
            
            compare_link = None
            for locator in compare_locators:
                try:
                    compare_link = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located(locator)
                    )
                    # Scroll element into view if it's hidden
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", compare_link)
                    break
                except Exception:
                    continue
            
            if compare_link:
                # Try to wait for it to be clickable
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(compare_link))
                try:
                    compare_link.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", compare_link)
            else:
                raise Exception("Compare button not found")
        except Exception:
            # Navigating directly to compare page
            self.visit("index.php?route=product/compare")
        self.wait_for_page_ready()

    def get_compare_items_count(self):
        """Get the number of items in compare list"""
        try:
            items = self.finds(*self.COMPARE_ITEMS, timeout=5)
            # Filter out header rows if any
            return len([item for item in items if item.text.strip()])
        except Exception:
            return 0

    def has_compare_items(self):
        """Check if compare page has any items"""
        count = self.get_compare_items_count()
        return count > 0

    def is_empty(self):
        """Check if compare page is empty"""
        try:
            empty_msg = self.find(*self.EMPTY_MESSAGE, timeout=5)
            return "empty" in empty_msg.text.lower() or "no products" in empty_msg.text.lower()
        except Exception:
            return not self.has_compare_items()

    def remove_item(self, index=0):
        """Remove an item from compare list"""
        try:
            remove_buttons = self.finds(*self.REMOVE_BUTTON)
            if remove_buttons and len(remove_buttons) > index:
                try:
                    remove_buttons[index].click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", remove_buttons[index])
                self.wait_for_page_ready()
                return True
        except Exception:
            return False
        return False

    def get_success_message(self, timeout=5):
        """Get success message text after removing a product"""
        try:
            # First try CSS selector for alert-success
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.SUCCESS_MESSAGE)
            )
            message = self.driver.find_element(*self.SUCCESS_MESSAGE)
            text = message.text.strip()
            # Remove the close button '×' if present
            text = text.replace('×', '').strip()
            if text:
                return text
        except Exception:
            pass
        
        # Try XPath selectors that specifically look for the success message
        try:
            success_xpath_selectors = [
                "//*[contains(@class, 'alert-success')]",
                "//*[contains(@class, 'alert') and contains(@class, 'success')]",
                "//*[contains(text(), 'Success') and contains(text(), 'modified')]",
                "//*[contains(text(), 'You have modified your product comparison')]",
                "//div[contains(@class, 'alert-success')]",
                "//*[contains(text(), 'Success:')]"
            ]
            
            for xpath in success_xpath_selectors:
                try:
                    message = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    text = message.text.strip()
                    # Remove the close button '×' if present
                    text = text.replace('×', '').strip()
                    if text:
                        return text
                except Exception:
                    continue
        except Exception:
            pass
        
        return None

   
    def get_product_names(self):
        """Getting list of product names in compare table """
        try:
            product_names = []
            seen_names = set()
            
            #  Looking for product names in the first row of the table (header row with product names)
            try:
                # Finding the table
                table = self.driver.find_element(By.CSS_SELECTOR, "table#compare-products, #content table, .table-responsive table")
                
                # Getting all table headers (th) or first row cells (td)
                first_row_selectors = [
                    "thead tr th a[href*='product/product']",
                    "thead tr th strong",
                    "tbody tr:first-child td a[href*='product/product']",
                    "tbody tr:first-child td strong",
                    "tr:first-child td a[href*='product/product']",
                    "tr:first-child td strong"
                ]
                
                for selector in first_row_selectors:
                    try:
                        elements = table.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            href = elem.get_attribute("href") or ""
                            
                            # Skip if empty, contains "Remove", already seen, or is a remove link
                            if (text and text.lower() != "remove" and "remove" not in text.lower() 
                                and "remove" not in href.lower() and text not in seen_names):
                                product_names.append(text)
                                seen_names.add(text)
                        if product_names:
                            break
                    except Exception:
                        continue
                
                # If no products found, looking at all rows but filter properly
                if not product_names:
                    try:
                        # Finding all product links in table cells (excluding remove links)
                        all_links = table.find_elements(By.CSS_SELECTOR, "td a[href*='product/product']:not([href*='remove'])")
                        for link in all_links:
                            text = link.text.strip()
                            href = link.get_attribute("href") or ""
                            
                            # Adding unique product names that are not "Remove"
                            if (text and text.lower() != "remove" and "remove" not in text.lower() 
                                and "remove" not in href.lower() and text not in seen_names):
                                product_names.append(text)
                                seen_names.add(text)
                    except Exception:
                        pass
                        
            except Exception:
                # Trying direct selectors if table structure is different
                selectors = [
                    "table#compare-products td strong",
                    "table#compare-products td a[href*='product/product']:not([href*='remove'])",
                    "#content table td strong",
                    "#content table td a[href*='product/product']:not([href*='remove'])",
                    ".table-responsive table td strong",
                    ".table-responsive table td a[href*='product/product']:not([href*='remove'])",
                ]
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            href = elem.get_attribute("href") or ""
                            
                            if (text and text.lower() != "remove" and "remove" not in text.lower() 
                                and "remove" not in href.lower() and text not in seen_names):
                                product_names.append(text)
                                seen_names.add(text)
                        if product_names:
                            break
                    except Exception:
                        continue
            
            return product_names
        except Exception:
            return []

    def is_page_loaded(self):
        """Check if compare page is loaded"""
        try:
            # Check for either compare table or empty message
            self.driver.find_element(*self.COMPARE_TABLE)
            return True
        except Exception:
            try:
                self.driver.find_element(*self.EMPTY_MESSAGE)
                return True
            except Exception:
                return False