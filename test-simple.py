import unittest
from server import app
from model import connect_to_db, db, User, Log, Location, Type, LocationType 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

##############################


# browser = webdriver.Chrome('/Users/Sarah/Downloads/chromedriver')
# browser.get('http://localhost:5000')

# test if browser title matches assumed page title
# assert browser.title == 'Project', 'Browser title was ' + browser.title

class ProjectTestFunctional(unittest.TestCase):
    """Tests for Hackbright Project"""

    def setUp(self):
        self.browser = webdriver.Chrome('/Users/Sarah/Downloads/chromedriver')
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    # def test_homepage_title(self):
    #     """Test for correct browser page title"""

    #     self.browser.get('http://localhost:5000')
    #     self.assertEqual('Project', self.browser.title)
    #     # self.fail('Finish the test!')

    def test_signup_form(self):

        self.browser.get('http://localhost:5000')
        lnk = self.browser.find_element_by_id('signupLink')
        lnk.click()

        try:
            element = self.browser.find_element_by_id('signup')
            if element.is_displayed():
                print 'Element found on page'
            else:
                self.fail('Element not on page')
        except NoSuchElementException:
            print 'Not an element exception'
            return False



# class ProjectTestUnit(unittest.TestCase):
#     """Unit tests for Hackbright Project"""

#     def setUp(self):
#         app.config['TESTING'] = True
#         app.config['SECRET_KEY'] = 'key'
#         self.client = app.test_client()

#     def test_homepage(self):
#         """Test to see if home page text appears"""
#         result = self.client.get('/')
#         self.assertIn('Go do the things', result.data)


# class ProjectTestDatabase(unittest.TestCase):
#     """Tests that use the database"""

#     def setUp(self):
#         self.client = app.test_client()
#         app.config['TESTING'] = True
#         connect_to_db(app, "postgresql:///testdb")
#         app.config['SECRET_KEY'] = 'ABC'

#     def tearDown(self):
#         db.session.close()

#     def test_login(self):
#         """test if user can login and see profile page info"""
#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['user'] = 'bbuilder'
#                 sess['home_lat'] = '37.794434'
#                 sess['home_long'] = '-122.39520160000001'
#             result = c.get('/', follow_redirects=True)
#             self.assertIn('Welcome back', result.data)

if __name__ == "__main__":
    unittest.main()