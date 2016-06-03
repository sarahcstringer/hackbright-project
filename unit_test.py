import unittest
from server import app
from model import example_data, connect_to_db, db, User, Log, Location, Type, LocationType 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import helper


class UnitTest(unittest.TestCase):
    def test_format_time(self):
        test_time_1 = helper.format_time([u'12:00', u'AM'])
        test_time_2 = helper.format_time([u'2:00', u'PM'])
        self.assertEqual(test_time_1, '00:00')
        self.assertEqual(test_time_2, '14:00')



    def test_check_overlap_times(self):
        test_times_1 = helper.check_overlap_times([('15:00', '16:00')], '12:00', 
                                '14:30')
        test_times_2 = helper.check_overlap_times(['12:00', '14:00'], '10:00',
                                '17:00')
        self.assertNotEqual(test_times_1, 'False')
        self.assertEqual(test_times_2, 'False')

    def test_format_date(self):
        # test_date_1 = helper.format_date({'dateRequest': 'datepicker'})
        test_date_2 = helper.format_date({'dateRequest': 'next',
                                    'showDate': 'Sunday, May 29, 2016'})
        self.assertEqual(test_date_2, '2016-05-30')

class ProjectTestDatabase(unittest.TestCase):
    """Tests that use the database"""

    def setUp(self):

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()


        # self.client = app.test_client()
        # app.config['TESTING'] = True
        # app.config['SECRET_KEY'] = 'ABC'

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_check_login(self):
        login_return_1 = helper.check_login('bbuild', 'password')
        login_return_2 = helper.check_login('bbuilder', 'hi')
        self.assertEqual(login_return_1, 'True')
        self.assertEqual(login_return_2, 'False')

    def test_check_username(self):
        username_test_1 = helper.check_username_exists('bbuild')
        self.assertEqual(username_test_1, 'True')
        self.assertEqual(helper.check_username_exists('bbuilder'), 'False')


if __name__ == '__main__':
    unittest.main()