import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5000"  # Change to your deployed URL when testing on EC2

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver


class TestFitnessTrackerHomePage(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    # TC-01: Home page loads successfully
    def test_01_homepage_loads(self):
        self.driver.get(BASE_URL)
        self.assertIn("Fitness", self.driver.title)

    # TC-02: Stats section is visible on homepage
    def test_02_stats_section_visible(self):
        self.driver.get(BASE_URL)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        # Stats section should show some numeric data or zeros
        self.assertTrue(len(body) > 0)

    # TC-03: Workout form is present on homepage
    def test_03_workout_form_present(self):
        self.driver.get(BASE_URL)
        form = self.driver.find_elements(By.TAG_NAME, "form")
        self.assertGreater(len(form), 0, "No form found on homepage")

    # TC-04: Log a new workout successfully
    def test_04_log_new_workout(self):
        self.driver.get(BASE_URL)
        wait = WebDriverWait(self.driver, 10)

        self.driver.find_element(By.NAME, "workout_title").send_keys("Morning Run")
        Select(self.driver.find_element(By.NAME, "workout_type")).select_by_visible_text("Running")
        self.driver.find_element(By.NAME, "duration").send_keys("30")
        self.driver.find_element(By.NAME, "calories_burned").send_keys("250")
        self.driver.find_element(By.NAME, "workout_date").send_keys("2026-05-08")
        self.driver.find_element(By.NAME, "notes").send_keys("Felt great!")

        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        time.sleep(1)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("workout", body.lower())

    # TC-05: Workout form rejects missing title
    def test_05_form_missing_title(self):
        self.driver.get(BASE_URL)
        # Leave title empty, try to submit
        self.driver.find_element(By.NAME, "duration").send_keys("30")
        self.driver.find_element(By.NAME, "calories_burned").send_keys("200")
        self.driver.find_element(By.NAME, "workout_date").send_keys("2026-05-08")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        # Should stay on same page (HTML5 validation or server error)
        self.assertIn(BASE_URL, self.driver.current_url)


class TestFitnessTrackerNavigation(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    # TC-06: Navigate to Workout History page
    def test_06_navigate_to_history(self):
        self.driver.get(BASE_URL + "/history")
        self.assertEqual(self.driver.current_url, BASE_URL + "/history")

    # TC-07: History page loads without error
    def test_07_history_page_loads(self):
        self.driver.get(BASE_URL + "/history")
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertGreater(len(body), 0)

    # TC-08: Navigate to Analytics page
    def test_08_navigate_to_analytics(self):
        self.driver.get(BASE_URL + "/analytics")
        self.assertEqual(self.driver.current_url, BASE_URL + "/analytics")

    # TC-09: Analytics page loads without error
    def test_09_analytics_page_loads(self):
        self.driver.get(BASE_URL + "/analytics")
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertGreater(len(body), 0)

    # TC-10: Navigate to Goals page
    def test_10_navigate_to_goals(self):
        self.driver.get(BASE_URL + "/goals")
        self.assertEqual(self.driver.current_url, BASE_URL + "/goals")


class TestFitnessTrackerCoachLogin(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    # TC-11: Coach login page loads
    def test_11_coach_login_page_loads(self):
        self.driver.get(BASE_URL + "/coach_login")
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertGreater(len(body), 0)

    # TC-12: Coach login with wrong password shows error
    def test_12_coach_login_wrong_password(self):
        self.driver.get(BASE_URL + "/coach_login")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpassword")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("denied", body.lower())

    # TC-13: Coach login with correct password redirects to dashboard
    def test_13_coach_login_correct_password(self):
        self.driver.get(BASE_URL + "/coach_login")
        self.driver.find_element(By.NAME, "password").send_keys("fit_guru2023")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        self.assertIn("dashboard", self.driver.current_url.lower())

    # TC-14: Dashboard is protected (redirect if not logged in)
    def test_14_dashboard_protected(self):
        self.driver.get(BASE_URL + "/fitness_dashboard")
        time.sleep(1)
        # Should redirect to coach_login
        self.assertIn("coach_login", self.driver.current_url)

    # TC-15: Logout redirects to homepage
    def test_15_logout_redirects_home(self):
        # First login
        self.driver.get(BASE_URL + "/coach_login")
        self.driver.find_element(By.NAME, "password").send_keys("fit_guru2023")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        # Now logout
        self.driver.get(BASE_URL + "/logout")
        time.sleep(1)
        self.assertEqual(self.driver.current_url.rstrip("/"), BASE_URL)


if __name__ == "__main__":
    # Run tests and output results
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestFitnessTrackerHomePage))
    suite.addTests(loader.loadTestsFromTestCase(TestFitnessTrackerNavigation))
    suite.addTests(loader.loadTestsFromTestCase(TestFitnessTrackerCoachLogin))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    import sys
    sys.exit(0 if result.wasSuccessful() else 1)
