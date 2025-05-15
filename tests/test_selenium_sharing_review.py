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

    def test_sharing_review_and_comment(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        try:
            #login as testing (sender)
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()
            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            driver.find_element(By.NAME, "email").send_keys("testing@testing.com")
            driver.find_element(By.NAME, "password").send_keys("testing_password")
            time.sleep(3)
            driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
            time.sleep(3)

            #go to profile and share review
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "My Profile"))).click()
            time.sleep(2)
            checkboxes = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "share-checkbox")))
            checkbox = checkboxes[0]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
            time.sleep(3)
            checkbox.click()

            recipient_input = driver.find_element(By.ID, "recipientUserInput")
            recipient_input.send_keys("123")
            time.sleep(3)
            suggestions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#user-suggestions .list-group-item")))
            suggestions[0].click()
            time.sleep(3)

            share_button = driver.find_element(By.ID, "shareButton")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", share_button)
            time.sleep(3)
            share_button.click()
            time.sleep(3)

            wait.until(EC.presence_of_element_located((By.NAME, "comment")))
            driver.find_element(By.NAME, "comment").send_keys("let's go together someday")
            driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
            time.sleep(3)

            body = driver.find_element(By.TAG_NAME, "body").text
            self.assertIn("let's go together someday", body)

            #logout
            logout_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Logout")))
            logout_link.click()
            time.sleep(3)

            #login as 123 (recipient)
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()
            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            driver.find_element(By.NAME, "email").send_keys("123@testing.com")
            driver.find_element(By.NAME, "password").send_keys("1a2b3c")
            time.sleep(3)
            driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
            time.sleep(3)

            #go to sharing page
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sharing Page"))).click()
            time.sleep(3)

            #find and click 'View Conversation' for user 'testing'
            conversation_blocks = driver.find_elements(By.CSS_SELECTOR, ".list-group-item")
            found = False

            for block in conversation_blocks:
                if "testing" in block.text.lower():
                    view_link = block.find_element(By.XPATH, ".//a[contains(text(), 'View Conversation')]")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_link)
                    time.sleep(3)
                    view_link.click()
                    found = True
                    break

            self.assertTrue(found, "View Conversation link for user 'testing' was not found.")
            time.sleep(3)

            #leave a reply
            wait.until(EC.presence_of_element_located((By.NAME, "comment")))
            driver.find_element(By.NAME, "comment").send_keys("let's go")
            driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
            time.sleep(3)

            body = driver.find_element(By.TAG_NAME, "body").text
            self.assertIn("let's go", body)

        except Exception as e:
            print(f"Test failed: {e}")
            raise


if __name__ == "__main__":
    unittest.main()
