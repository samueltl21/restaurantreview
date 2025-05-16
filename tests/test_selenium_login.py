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

    def test_login_existing_user(self):
        driver = self.driver
        wait = WebDriverWait(driver, 3)

        try:
            #login
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()
            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            driver.find_element(By.NAME, "email").send_keys("testing@testing.com")
            driver.find_element(By.NAME, "password").send_keys("testing_password")
            time.sleep(2)
            driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()

            #checking that my profile is visible after login
            time.sleep(3)
            body = driver.find_element(By.TAG_NAME, "body").text
            self.assertIn("My Profile", body)

        except Exception as e:
            print(f"Login test failed: {e}")
            raise

if __name__ == "__main__":
    unittest.main()
