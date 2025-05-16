import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestNavigationFlow(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:5000/")
        time.sleep(1)

    def tearDown(self):
        time.sleep(2)
        self.driver.quit()

    def scroll_down_and_up(self, driver):
        """Scroll to bottom then back to top"""
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        time.sleep(2)
        driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
        time.sleep(2)

    def test_navigation_flow_scroll_and_footer(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        try:
            # Login
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()
            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            driver.find_element(By.NAME, "email").send_keys("testing@testing.com")
            driver.find_element(By.NAME, "password").send_keys("testing_password")
            driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
            time.sleep(2)

            # 1. Homepage scroll down and up
            driver.get("http://127.0.0.1:5000/")
            self.scroll_down_and_up(driver)
            self.assertIn("Discover Best Restaurants", driver.page_source)

            # Visit a restaurant detail page after homepage scroll
            driver.get("http://127.0.0.1:5000/restaurants/4")
            time.sleep(2)
            driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
            time.sleep(2)
            self.assertIn("Reviews", driver.page_source)

            # 2. Navigate to Sharing Page → scroll down and up
            driver.get("http://127.0.0.1:5000/shared_with")
            self.scroll_down_and_up(driver)
            self.assertIn("Sharing Page", driver.page_source)

            # 3. Navigate to My Profile → scroll down and up
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "My Profile"))).click()
            self.scroll_down_and_up(driver)
            self.assertIn("My Profile", driver.page_source)

            # 4. Navigate to Upload Review → scroll down only
            driver.get("http://127.0.0.1:5000/upload_reviews")
            driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
            self.scroll_down_and_up(driver)
            self.assertIn("Rate a Restaurant", driver.page_source)

            # 5. Click 'About Us' from the footer
            about_us_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "About Us")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", about_us_link)
            time.sleep(2)
            about_us_link.click()
            time.sleep(2)

            self.assertIn("About Us", driver.page_source)

        except Exception as e:
            print(f"Flow + scroll test failed: {e}")
            raise

if __name__ == "__main__":
    unittest.main()
