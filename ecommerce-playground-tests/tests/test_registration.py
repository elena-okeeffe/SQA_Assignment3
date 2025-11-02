import time, random, string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

REGISTER_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=account/register"

def unique_email():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    print("Creating email to be used...")
    return f"sumangala_{suffix}@example.com"

def click_js(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    driver.execute_script("arguments[0].click();", element)

def test_user_registration():
    email = unique_email()
    print(email)
    password = "Test@12345"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1300, 900)

    print("Working on the URL + field values to be set")

    try:
        driver.get(REGISTER_URL)

        # Fill fields
        driver.find_element(By.NAME, "firstname").send_keys("Sumangala")
        driver.find_element(By.NAME, "lastname").send_keys("Rao")
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "telephone").send_keys("0400000000")
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "confirm").send_keys(password)

        # Agree checkbox
        print("ticking the privacy - Agree") 
        agree = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "input-agree")))
        click_js(driver, agree)

        # Continue click
        print("Checking on Continue")
        cont = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue']"))
        )
        click_js(driver, cont)

        # Verify
        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element(
            (By.TAG_NAME, "body"), "Your Account Has Been Created!"
        ))
        assert "Your Account Has Been Created!" in driver.page_source
        print("!!!!!!!!!!!Test Passed...Registration Successful!!!!!!!!!!!!!")

    except Exception as e:
        print("!!!!!!!!!!Test Failed!!!!!!!!!!!!!:", e)
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    test_user_registration()
