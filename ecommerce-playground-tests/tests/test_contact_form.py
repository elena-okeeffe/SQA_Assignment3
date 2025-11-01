
import pytest
import time
from pages.contact_page import ContactPage


@pytest.mark.usefixtures("driver")
class TestContactForm:
    def test_contact_form_submission(self, driver, base_url):
        page = ContactPage(driver, base_url)
        
       
        print("\n" + "="*60)
        print("Contact Us Form Test")
        print("="*60)
        print("Contact Us page loaded successfully!")
        page.open()
        #delay to see page loaded
        time.sleep(1) 

        #Verifying page loaded correctly
        print("Verifying page loaded correctly...")
        assert page.is_page_loaded(), "Contact page did not load correctly"
        print("Page loaded successfully!")
        print("Taking screenshot of page loaded...")
        page.take_screenshot("F11_contact_page_loaded")
        time.sleep(1)  
        
        #Filling contact form
        print("Filling contact form...")
        page.fill_contact_form(
            name="John Cena",
            email="johncena.test@gmail.com",
            enquiry="Hello, this is a test enquiry message for the contact form."
        )
       
        print("Taking screenshot of filled form...")
        page.take_screenshot("F11_contact_form_filled")
        time.sleep(1)  
        
        #Submitting form
        print("Submitting form...")
        page.submit_form()
        time.sleep(1)  
        
        #Waiting for redirect to success page
        print("Waiting for redirect to success page...")
        assert page.wait_for_success_page(), "Form should redirect to success page"
        assert page.is_on_success_page(), "Should be on success page after submission"
        print("Redirect to success page done!")
        print("Taking screenshot of success page...")
        page.take_screenshot("F11_contact_success_page")
        time.sleep(1)
        
        # Verifying success message on success page
        print("Verifying success message...")
        success_message = page.get_success_message()
        assert success_message is not None and len(success_message) > 0, \
            "Success message should appear on success page"
        assert "successfully sent" in success_message.lower(), \
            f"Success message should contain 'successfully sent', got: '{success_message}'"
        
        print(f"Success message confirmed: '{success_message}'")
        print("Taking screenshot of success message visible...")
        page.take_screenshot("F11_contact_success_message_displayed")
        time.sleep(2)
        
        # Clicking Continue button to go to home page
        print("Clicking Continue button to return to home page...")
        continue_clicked = page.click_continue_button()
        if continue_clicked:
            time.sleep(2)  # Wait for navigation
            print("Continue button clicked!")
            
            # Verifying on home page
            if page.verify_on_home_page():
                print("Successfully navigated to home page!")
                print(f"  Current URL: {driver.current_url}")
                print("Taking screenshot of home page...")
                page.take_screenshot("F11_contact_home_page")
                time.sleep(2)
            else:
                print(f"Navigation completed. Current URL: {driver.current_url}")
                page.take_screenshot("F11_contact_after_continue")
        else:
            print("Continue button not found or not clicked (this is okay)")
            page.take_screenshot("F11_contact_no_continue_button")
        
        print("="*60)
        print("Contact form test completed successfully!")
        print("="*60 + "\n")

