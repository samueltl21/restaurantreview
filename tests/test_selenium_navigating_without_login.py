import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestGuestAccessFlow(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:5000/")
        time.sleep(1)

    def tearDown(self):
        time.sleep(2)
        self.driver.quit()

    def scroll_down_and_up(self, driver):
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        time.sleep(2)
        driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
        time.sleep(2)

    def test_guest_access_and_view_restaurant_detail(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        try:
            # 1. Homepage scroll to restaurant section (below banner)
            driver.get("http://127.0.0.1:5000/")
            driver.execute_script("window.scrollBy(0, 600);")  # Scroll past banner
            time.sleep(2)

            # Go to a known restaurant detail page
            driver.get("http://127.0.0.1:5000/restaurants/4")
            time.sleep(2)
            self.assertIn("Reviews", driver.page_source)  # or use known restaurant name

            # Scroll to bottom of restaurant page
            driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
            time.sleep(2)

            # 2. Access protected page: shared_with
            driver.get("http://127.0.0.1:5000/shared_with")
            time.sleep(2)
            self.assertIn("Login", driver.page_source)

            # 3. Access profile
            driver.get("http://127.0.0.1:5000/profile")
            time.sleep(2)
            self.assertIn("Login", driver.page_source)

            # 4. Access upload_reviews
            driver.get("http://127.0.0.1:5000/upload_reviews")
            time.sleep(2)
            self.assertIn("Login", driver.page_source)

            about_us_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "About Us")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", about_us_link)
            time.sleep(2)
            about_us_link.click()
            time.sleep(2)
            self.assertIn("About Us", driver.page_source)

        except Exception as e:
            print(f"Guest access test failed: {e}")
            raise

if __name__ == "__main__":
    unittest.main()