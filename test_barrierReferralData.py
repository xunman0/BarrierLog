from barrierReferralData import BarrierReferralData
import unittest

x = BarrierReferralData()

class TestBarrierData(unittest.TestCase):
    """
    This suite of tests validates the response and methods of the BarrierReferralData class.
    Tests:
        test_Response : test for succesfull API call
        test_ActiveEntires : tests for correct amount of active entires
        test_Cols : test to make sure the pandas dataframe contains the correct columns
        test_UpdateData : tests for correct functionality of updateData()
        test_ExtractZipcode : tests for correct zipcode extraction of _extractZipcode()
    """
    def test_Response(self):
        # success message
        result = x.response['message']
        self.assertEqual(result, 'success')

        # 200 code
        result = x.response['message']
        self.assertEqual(result, 'success')

    def test_ActiveEntires(self):
        # num of active entires
        result = x.meta['active_entries']
        active_entries = len([x.response['content'][i]['status'] for i in range(len(x.response['content'])) if x.response['content'][i]['status'] == 'ACTIVE'])
        self.assertEqual(result, active_entries)

    def test_Cols(self):
        result = list(x.data.columns)
        cols = ['date', 'submission_type', 'age', 'sex', 'ethnicity', 'barrier_description', 'barrier_list', 
                     'barrier_cause', 'barrier_solution', 'solution_path', 'referring_org', 
                     'referring_staff', 'staff_email', 'staff_phone','family_contact', 'family_address', 
                     'family_phone', 'family_email','zipcode']
        self.assertEqual(result, cols)

    def test_UpdateData(self):
        # save orignal limit left
        original_limit = x.meta['limit_left']

        # update the data
        x.updateData()

        # save the new updated limit
        new_limit = x.meta['limit_left']

        self.assertEqual(original_limit-new_limit, 1)

    def test_ExtractZipcode(self):
        address_one = '1106 N Aspen Ave Eastvale, CA, 92880'
        address_two = 'Cherry St 92831 Ojai, CA'

        zipcode_one = x._extractZipcode(address_one)
        zipcode_two = x._extractZipcode(address_two)

        self.assertEqual(zipcode_one, '92880')
        self.assertEqual(zipcode_two, '92831')

if __name__ == '__main__':
    unittest.main()
