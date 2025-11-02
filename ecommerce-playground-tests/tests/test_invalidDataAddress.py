import os, time, random, string, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

PREFERRED_COUNTRY = os.getenv("COUNTRY", "Australia")
PREFERRED_REGION  = os.getenv("REGION", "New South Wales")

BASE         = "https://ecommerce-playground.lambdatest.io"
REGISTER_URL = f"{BASE}/index.php?route=account/register"
ADDRESS_URL  = f"{BASE}/index.php?route=account/address/add"

def unique_email():
    return f"sumangala_{''.join(random.choices(string.ascii_lowercase+string.digits, k=7))}@example.com"

def setup_browser():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    d.set_window_size(1300, 900)
    return d

def js_select_non_disabled_by_text(driver, select_css, wanted_text=None):
    script = """
    const sel = document.querySelector(arguments[0]);
    if (!sel) return {ok:false, reason:'select-not-found'};
    const want = (arguments[1] || '').toLowerCase();
    let idx = -1, chosen = null;
    for (let i=0;i<sel.options.length;i++){
      const opt = sel.options[i];
      if (opt.disabled || opt.value === '') continue;
      const txt = opt.text.trim();
      if (!want || txt.toLowerCase() === want || txt.toLowerCase().includes(want)){
        idx = i; chosen = txt; break;
      }
    }
    if (idx === -1){
      // fallback: first non-disabled, non-empty option
      for (let i=0;i<sel.options.length;i++){
        const opt = sel.options[i];
        if (!opt.disabled && opt.value !== '') { idx = i; chosen = opt.text.trim(); break; }
      }
    }
    if (idx === -1) return {ok:false, reason:'no-valid-option'};
    sel.selectedIndex = idx;
    sel.dispatchEvent(new Event('change', {bubbles:true}));
    return {ok:true, text: chosen};
    """
    result = driver.execute_script(script, select_css, wanted_text or "")
    if not result or not result.get("ok"):
        raise RuntimeError(f"JS select failed: {result}")
    return result["text"]

def wait_present(d, by, locator, timeout=12):
    return WebDriverWait(d, timeout).until(EC.presence_of_element_located((by, locator)))

def register_user(d, email, password):
    print("Creating a Registered User for the test")
    d.get(REGISTER_URL)
    d.find_element(By.NAME, "firstname").send_keys("Sumangala")
    d.find_element(By.NAME, "lastname").send_keys("Rao")
    d.find_element(By.NAME, "email").send_keys(email)
    d.find_element(By.NAME, "telephone").send_keys("0400000000")
    d.find_element(By.NAME, "password").send_keys(password)
    d.find_element(By.NAME, "confirm").send_keys(password)

    label = wait_present(d, By.CSS_SELECTOR, "label[for='input-agree']")
    d.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", label)

    cont = WebDriverWait(d, 12).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue']")))
    d.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", cont)

    WebDriverWait(d, 12).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Your Account Has Been Created!")
    )
    print("Registered and authenticated")

def select_country_and_region(driver, country_text, region_text):
    # Country first (JS based, non-disabled)
    print(f"Selecting country: {country_text}")
    wait_present(driver, By.NAME, "country_id")
    chosen_country = js_select_non_disabled_by_text(driver, "select[name='country_id']", country_text)

    # Wait for region select to appear and populate
    wait_present(driver, By.NAME, "zone_id")
    # Poll until it has a non-disabled, non-empty option
    end = time.time() + 12
    while time.time() < end:
        sel = Select(driver.find_element(By.NAME, "zone_id"))
        valid = [o for o in sel.options if not o.get_attribute("disabled") and o.get_attribute("value").strip()]
        if valid:
            break
        time.sleep(0.3)
    if not valid:
        raise TimeoutException("Region list did not populate")

    # Region (JS based, non-disabled, with fallback)
    print(f"Selecting region (pref): {region_text}")
    chosen_region = js_select_non_disabled_by_text(driver, "select[name='zone_id']", region_text)
    return chosen_country, chosen_region


def test_invalid_address():
    email = unique_email()
    password = "Test@12345"
    d = setup_browser()

    try:
        register_user(d, email, password)

        print("Opening Add Address form")
        d.get(ADDRESS_URL)
        wait_present(d, By.NAME, "firstname")

        print("Entering special characters and invalid data into required address fields")
        d.find_element(By.NAME, "firstname").send_keys("1234567")
        d.find_element(By.NAME, "lastname").send_keys("3454")
        d.find_element(By.NAME, "company").send_keys("~!!")
        d.find_element(By.NAME, "address_1").send_keys("!@##")
        d.find_element(By.NAME, "city").send_keys("&*(()")
        d.find_element(By.NAME, "postcode").send_keys("(*&^")
       
        try:
            c, r = select_country_and_region(d, PREFERRED_COUNTRY, PREFERRED_REGION)
        except Exception as e:
            print(f"Preferred country/region failed ({e}). Trying fallback: Australia / New South Wales")
            c, r = select_country_and_region(d, "Australia", "New South Wales")
        print(f"Chosen: {c} / {r}")

        # Default Yes?
        default_yes = d.find_element(By.CSS_SELECTOR, "input[name='default'][value='1']")
        d.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", default_yes)

        # Save action
        save = WebDriverWait(d, 12).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue']")))
        d.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", save)

        # EXPECTATION: Should NOT navigate to Address Book; if it does → bug
        time.sleep(2)
        if "Address Book" in d.page_source:
            print("!!!!!!!!!!! Test Failed and Bug found: Address with invalid data was saved successfully (validation missing)!!!!!!!!!!!!!")
        else:
            log.info("!!!!!!!!!!Test Passed - Input Validation prevented save (expected behaviour)!!!!!!!!!!!!!!")

    finally:
        d.quit()

if __name__ == "__main__":
    test_invalid_address()

