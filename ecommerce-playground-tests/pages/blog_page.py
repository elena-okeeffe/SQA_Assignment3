# pages/blog_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage
import time

class BlogPage(BasePage):
    COMMENT_NAME_FIELD = (By.ID, "input-name")
    COMMENT_EMAIL_FIELD = (By.ID, "input-email")
    COMMENT_TEXT_FIELD = (By.ID, "input-comment")
    COMMENT_SUBMIT_BUTTON = (By.ID, "button-comment")
    ARTICLE_TITLE = (By.CSS_SELECTOR, "h1, h2, .article-title, .post-title")
    COMMENT_SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-success.alert-dismissible, .alert.alert-success, .success, .text-success")
    COMMENT_SUCCESS_ALERT = (By.CSS_SELECTOR, "#form-comment .alert.alert-success.alert-dismissible, form#form-comment .alert.alert-success")
    COMMENT_ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-danger, .text-danger, .error")

    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)

    def open_article(self, article_id=37):
        """Open a specific blog article"""
        self.visit(f"index.php?route=extension/maza/blog/article&article_id={article_id}")
        self.wait_for_page_ready()
        self._dismiss_overlays()

    def scroll_to_comment_form(self):
        """Scroll directly to the comment form element"""
        try:
            # Try to find container with data-id 
            form_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-id and contains(@class, 'content-comment-form')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form_container)
            time.sleep(0.5)
            return form_container
        except Exception:
            try:
                # Try to find form-comment by ID
                form = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "form-comment"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form)
                time.sleep(0.5)
                return form
            except Exception:
                try:
                   
                    comment_title = self.driver.find_element(By.XPATH, "//h4[contains(text(), 'Write a comment')]")
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", comment_title)
                    time.sleep(0.5)
                    return comment_title
                except Exception:
                    try:
                        # Try to find container with data-id attribute
                        form_container = self.driver.find_element(By.CSS_SELECTOR, "div[data-id][id*='entry'], div[class*='comment-form']")
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form_container)
                        time.sleep(0.5)
                        return form_container
                    except Exception:
                        # Fallback: scroll to bottom
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(0.5)
                        return None

    def fill_comment_form(self, name: str, email: str, comment: str):
        """Fill the comment form with provided data"""
        # Scroll to comment form if not already visible
        self.scroll_to_comment_form()
        
        # Wait for comment form to be visible
        try:
            self.wait.until(EC.presence_of_element_located(self.COMMENT_NAME_FIELD))
        except Exception:
            pass
        
        # Fill name field
        try:
            name_el = self.find(*self.COMMENT_NAME_FIELD)
            name_el.clear()
            name_el.send_keys(name)
        except Exception:
            # Try by name attribute
            try:
                name_el = self.driver.find_element(By.NAME, "name")
                name_el.clear()
                name_el.send_keys(name)
            except Exception:
                pass
        
        # Fill email field
        try:
            email_el = self.find(*self.COMMENT_EMAIL_FIELD)
            email_el.clear()
            email_el.send_keys(email)
        except Exception:
            try:
                email_el = self.driver.find_element(By.NAME, "email")
                email_el.clear()
                email_el.send_keys(email)
            except Exception:
                pass
        
        # Fill comment field
        try:
            comment_el = self.find(*self.COMMENT_TEXT_FIELD)
            comment_el.clear()
            comment_el.send_keys(comment)
        except Exception:
            try:
                comment_el = self.driver.find_element(By.NAME, "text")
                comment_el.clear()
                comment_el.send_keys(comment)
            except Exception:
                try:
                    comment_el = self.driver.find_element(By.NAME, "comment")
                    comment_el.clear()
                    comment_el.send_keys(comment)
                except Exception:
                    pass

    def submit_comment(self):
        """Submit the comment form"""
        try:
            btn = self.find(*self.COMMENT_SUBMIT_BUTTON)
            try:
                btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "button#button-comment")
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
            except Exception:
                pass
        self.wait_for_page_ready()
        time.sleep(1)

    def wait_for_success_alert(self, timeout=10):
        """Wait for the success alert to appear inside the form and scroll to it"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.presence_of_element_located(self.COMMENT_SUCCESS_ALERT))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", alert)
            time.sleep(0.5)
            return alert
        except Exception:
            try:
                wait = WebDriverWait(self.driver, timeout)
                alert = wait.until(EC.presence_of_element_located(self.COMMENT_SUCCESS_MESSAGE))
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", alert)
                time.sleep(0.5)
                return alert
            except Exception:
                return None

    def ensure_success_alert_visible(self):
        """Ensure the success alert is visible in viewport for screenshot"""
        try:
            form = self.driver.find_element(By.ID, "form-comment")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form)
            time.sleep(0.5)
            
            try:
                alert = form.find_element(By.CSS_SELECTOR, ".alert.alert-success.alert-dismissible, .alert.alert-success")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", alert)
                time.sleep(0.5)
                return True
            except Exception:
                return True
        except Exception:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            return False

    def get_success_message(self, timeout=10):
        """Get success message text after comment submission
        Expected message: 'Thank you for your comment. It has been submitted to the webmaster for approval.'
        """
        try:
            alert = self.wait_for_success_alert(timeout)
            if alert:
                text = alert.text.strip().replace('×', '').strip()
                if text and 'thank you' in text.lower() and 'webmaster' in text.lower():
                    return text
        except Exception:
            pass
        
        try:
            success_xpath_selectors = [
                "//form[@id='form-comment']//div[contains(@class, 'alert-success')]",
                "//*[contains(text(), 'Thank you for your comment') and contains(text(), 'submitted to the webmaster')]",
                "//*[contains(@class, 'alert-success') and contains(@class, 'alert-dismissible')]",
            ]
            
            for xpath in success_xpath_selectors:
                try:
                    message = WebDriverWait(self.driver, 2).until(
                        EC.visibility_of_element_located((By.XPATH, xpath))
                    )
                    text = message.text.strip().replace('×', '').strip()
                    if text and 'thank you' in text.lower() and 'webmaster' in text.lower():
                        return text
                except Exception:
                    continue
        except Exception:
            pass
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            el = wait.until(EC.visibility_of_element_located(self.COMMENT_SUCCESS_MESSAGE))
            text = el.text.strip().replace('×', '').strip()
            if text and 'thank you' in text.lower() and 'webmaster' in text.lower():
                return text
        except Exception:
            pass
        
        try:
            alerts = self.driver.find_elements(By.CSS_SELECTOR, "#form-comment .alert, .alert.alert-success")
            for alert in alerts:
                text = alert.text.strip().replace('×', '').strip()
                if text and 'thank you' in text.lower() and 'webmaster' in text.lower():
                    return text
        except Exception:
            pass
        
        return None

    def get_error_message(self, timeout=5):
        """Get error message if comment submission fails"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            el = wait.until(EC.visibility_of_element_located(self.COMMENT_ERROR_MESSAGE))
            return el.text.strip()
        except Exception:
            return None

    def is_article_loaded(self):
        """Check if blog article page is loaded"""
        try:
            self.find(*self.ARTICLE_TITLE)
            return True
        except Exception:
            return False

    def get_article_title(self):
        """Get the article title"""
        try:
            title_el = self.find(*self.ARTICLE_TITLE)
            return title_el.text.strip()
        except Exception:
            return None
