import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestEditReview(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:5000/")
        time.sleep(1)

    def tearDown(self):
        time.sleep(2)
        self.driver.quit()

    def test_edit_existing_review_modal(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        try:
            #login
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()
            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            driver.find_element(By.NAME, "email").send_keys("testing@testing.com")
            driver.find_element(By.NAME, "password").send_keys("testing_password")
            driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
            time.sleep(2)

            #go to profile page
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "My Profile"))).click()
            time.sleep(2)

            #scroll down to find edit button
            driver.execute_script("window.scrollBy(0, 500);")  #adjust scroll distance if needed
            time.sleep(2)
            edit_buttons = driver.find_elements(By.CLASS_NAME, "edit-review-btn")
            self.assertGreater(len(edit_buttons), 0, "No edit buttons found.")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_buttons[0])
            time.sleep(1)
            edit_buttons[0].click()
            time.sleep(2)

            #update fields
            wait.until(EC.visibility_of_element_located((By.ID, "editReviewModal")))
            driver.find_element(By.ID, "edit-rating").clear()
            driver.find_element(By.ID, "edit-rating").send_keys("4")
            driver.find_element(By.ID, "edit-spend").clear()
            driver.find_element(By.ID, "edit-spend").send_keys("35.50")
            driver.find_element(By.ID, "edit-comment").clear()
            driver.find_element(By.ID, "edit-comment").send_keys("Updated via Selenium!")

            #submit the form
            driver.find_element(By.ID, "editReviewForm").submit()
            time.sleep(3)

        except Exception as e:
            print(f"Edit review modal test failed: {e}")
            raise

if __name__ == "__main__":
    unittest.main()