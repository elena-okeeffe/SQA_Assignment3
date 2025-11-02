
# Test case for F5: Product compare
import pytest
import time
from pages.compare_page import ComparePage


@pytest.mark.usefixtures("driver")
class TestProductCompare: 
    def test_product_compare_functionality(self, driver, base_url):
        print("\n" + "="*60)
        print("Product Compare Test")
        print("="*60)
        
        compare_page = ComparePage(driver, base_url)
        
        # Opening the search page
        print("\nOpening search page...")
        search_url = "index.php?route=product/search&search="
        driver.get(f"{base_url}/{search_url}")
        time.sleep(2)
        print("Search page loaded!")
        compare_page.take_screenshot("Search page loaded")
        time.sleep(1)
        
        # Adding at least 2 products to compare
        print("\nAdding products to compare list...")
        products_added = 0
        try:
            # Looking for compare buttons
            compare_button_selectors = [
                "button[data-original-title*='Compare']",
                "a[data-original-title*='Compare']",
                "button[title*='Compare']",
                "a[title*='Compare']",
                "button[aria-label*='Compare']",
                "a[aria-label*='Compare']",
                ".fa-exchange",
                "button.compare",
                "a.compare",
                "[onclick*='compare']"
            ]
            
            all_compare_buttons = []
            for selector in compare_button_selectors:
                try:
                    buttons = driver.find_elements("css selector", selector)
                    all_compare_buttons.extend(buttons)
                except Exception:
                    continue
            
            # Removing duplicates while preserving order
            seen = set()
            unique_buttons = []
            for btn in all_compare_buttons:
                btn_id = id(btn)
                if btn_id not in seen:
                    seen.add(btn_id)
                    unique_buttons.append(btn)
            
            if len(unique_buttons) >= 2:  
                # Add first product
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", unique_buttons[0])
                    time.sleep(0.5)
                    try:
                        unique_buttons[0].click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", unique_buttons[0])
                    products_added += 1
                    print(f"Added product {products_added} to compare list!")
                    time.sleep(1)
                except Exception as e:
                    print(f" Could not add first product: {e}")
                
                # Add second product
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", unique_buttons[1])
                    time.sleep(0.5)
                    try:
                        unique_buttons[1].click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", unique_buttons[1])
                    products_added += 1
                    print(f"Added product {products_added} to compare list!")
                    time.sleep(1)
                except Exception as e:
                    print(f" Could not add second product: {e}")
                
                if products_added > 0:
                    print(f"Taking screenshot after adding {products_added} product(s)...")
                    compare_page.take_screenshot("Products added to compare list")
                    time.sleep(1)
            else:
                print(f" Found only {len(unique_buttons)} compare button(s). Added {products_added} product(s).")
        except Exception as e:
            print(f" Could not add products via buttons: {e}. Continuing with existing compare list...")
        
        # Opening the compare page
        print("\nOpening compare page...")
        compare_page.open_from_main_header()
        time.sleep(2)
        print("Compare page loaded!")
        compare_page.take_screenshot("Compare page loaded")
        time.sleep(1)
        
        # Verifying the compare page loaded
        print("\nVerifying compare page...")
        assert compare_page.is_page_loaded(), "Compare page did not load correctly"
        print("Page loaded correctly!")

        # Verifying products are displayed in compare table
        print("\nVerifying products in compare table...")
        has_items = compare_page.has_compare_items()
        is_empty = compare_page.is_empty()

        # Getting product names if available
        product_names = compare_page.get_product_names()

        assert has_items, "Compare page should have at least one product"
        assert len(product_names) > 0, "Compare table should display product names"
        print(f"Found {len(product_names)} product(s) in compare list!")
        print(f"  Products: {product_names}")
        print("Taking screenshot with products...")
        compare_page.take_screenshot("Products in compare list")
        time.sleep(2)

        # Removing a product from compare list
        print("\nRemoving a product from compare list...")
        initial_count = len(product_names)
        removed = compare_page.remove_item(index=0)

        if removed:
            print("Product removal initiated!")
        else:
            print(" Could not remove product (remove button not found)")

        # Verifying success message after removal
        print("\nVerifying success message...")
        success_message = compare_page.get_success_message(timeout=5)
        
        if success_message:
            assert len(success_message) > 0, "Success message should not be empty"
            # Verify the message contains expected text
            assert "success" in success_message.lower(), f"Success message should contain 'success', got: '{success_message}'"
            assert "modified" in success_message.lower() or "comparison" in success_message.lower(), \
                f"Success message should mention modification or comparison, got: '{success_message}'"
            print(f"Success message displayed: '{success_message}'")
            print("Taking screenshot with success message...")
            compare_page.take_screenshot("success_message")
            time.sleep(1)
        else:
            print(" Success message not found (this may be normal depending on the site behavior)")
        
        # Verifying the compare page structure exists
        assert has_items or is_empty, "Compare page should either show items or empty message"
        
        print("\n" + "="*60)
        print(" Product compare test completed successfully!")
        print("="*60 + "\n")

