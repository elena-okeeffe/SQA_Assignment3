# tests/test_register_existing_email.py
import pytest
from pages.register_page import RegisterPage

@pytest.mark.usefixtures("driver")
class TestRegisterExistingEmail:
    #This test is for Function F14 Unique User Emails
    def test_register_with_existing_email_shows_warning(self, driver):
        page = RegisterPage(driver, base_url="https://ecommerce-playground.lambdatest.io/")
        page.open_from_home()
        # fill using the CSV test data: first/last/email/telephone/password
        page.fill_registration_form(
            first="First",
            last="Last",
            email="firstlast@gmail.com",
            telephone="98765432",
            password="Password123!"
        )
        page.agree_privacy()
        page.submit()

        alert_text = page.get_alert_text(timeout=8)
        assert alert_text, "Expected an alert to appear after submitting registration"
        assert "E-Mail Address is already registered" in alert_text or "already registered" in alert_text, \
            f"Unexpected alert text: {alert_text}"
        print(f"PASS: Registration with existing email produced expected alert: '{alert_text}'")
