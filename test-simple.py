import unittest
from server import app
from model import connect_to_db, db, User, Log, Location, Type, LocationType 
from selenium import webdriver

browser = webdriver.Chrome('/Users/Sarah/Downloads/chromedriver')
browser.get('http://localhost:5000')

# test if browser title matches assumed page title
assert browser.title == 'Project'

# class ProjectTest(unittest.TestCase):
#     """Tests for Hackbright Project"""

#     def setUp(self):
#         self.client = app.test_client()
#         app.config['TESTING'] = True

#     def test_homepage(self):
#         result = self.client.get('/')
#         self.assertIn('Go do the', result.data)

# if __name__ == "__main__":
#     unittest.main()