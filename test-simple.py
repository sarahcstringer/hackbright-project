import unittest
from server import app
from model import connect_to_db, db, User, Log, Location, Type, LocationType 
from selenium import webdriver

# browser = webdriver.Chrome('/Users/Sarah/Downloads/chromedriver')
# browser.get('http://localhost:5000')

# # test if browser title matches assumed page title
# assert browser.title == 'Project', 'Browser title was ' + browser.title

class ProjectTest(unittest.TestCase):
    """Tests for Hackbright Project"""

    def setUp(self):
        self.browser = webdriver.Chrome('/Users/Sarah/Downloads/chromedriver')
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_homepage_title(self):
        """Test for correct browser page title"""

        self.browser.get('http://localhost:5000')
        self.assertEqual('Project', self.browser.title)
        # self.fail('Finish the test!')

if __name__ == "__main__":
    unittest.main()