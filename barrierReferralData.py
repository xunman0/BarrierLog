import pandas as pd
import requests
import re
import logging
import os
import ast
import streamlit as st

# constants for dynamic parsing
JOTFORM_FIELDS = ['Date', 'Referring Organization', 'Referring Staff Name', 'Family Contact Name', 
                  'Family Contact Address','Family Contact Phone Number', 'Family Contact Email',
                  'Barrier Description', 'Barriers', 'Cause of Barrier (optional)',
                  'Solution to Barrier (optional)', 'Solution Pathway to Barrier (optional)', 
                  'Referring Staff Email', 'Referring Staff Phone Number', 'Submission Type',
                    'Age', 'Sex', 'Ethnicity', 'Zipcode']
API_KEY = st.secrets["API_KEY"]
FORM_ID = st.secrets["FORM_ID"]



# Create a logger instance
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler('json_processing.log', 'w')
handler.setLevel(logging.DEBUG)

# Create a formatter and set the formatter for the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

class BarrierReferralData():
    """
    Class instance for the barrier referral form data. This class makes a call to the Jotform API,
    downloads the data, parses it, and stores the data in a pandas dataframe. It includes helper functions to parse the data and 
    class methods that aid in analysis, updating data, and retreiving meta data on the API/JSON response.
    Attributes:
        data : pandas dataframe containing all data (including contact information)
        response : contains the json response object
        meta : contains meta data on API limit, json keys, and active entries
        barriera : dataframe that contains the barrier data only (no contact information)
    Methods:
        updateData : updates all attributes, processes json from _callAPI(), and outputs a pandas dataframe
        barrierData : returns barrier data only (no PHI)
        topValues : takes _masterList() and returns a pd.Series with the top i values
        latestDate : returns the most recent date in the data
        info : creates meta data dict object and loads into self.meta
        _callAPI : calls Jotform API to load data as a JSON object
        _loadData : loads csv data and if not present, will call updateData()
        _createIndexFieldKey : creates the jotform_field_i : string_integer key-value pair that is necessary for dynamic parsing
        _masterList : creates a single list of values from a column of lists
        _parseAddress : uses regex to parse address data in json object
        _parseReferringOrg : parses the data related to the referral organization
        _parseFamily : parses the data related to the family contact
        _parseBarrierLog : parases the data related to barrier incidents
        _formatSubmissionTypeCol: Asserts/formats the three submission types: ['Barrier Log', 'Self-Referral', 'Organization Referral]
    """
    def __init__(self):
        """
        Constructor with no args.
        """
        self.data = self._loadData()
        self.response = self._callAPI()
        self.index_field_key = self._createIndexFieldKey(self.response)
        self.meta = self.info()
        self.barriers = self.barrierData()
        self.latestDate = self.latestDate()

    def _loadData(self):
        """
        This method loads the csv data into the self.data attribute and if the 
        csv is not present, will call updateData() (only called when class is instantiated).
        Args:
            None
        Returns:
            data (pandas.dataframe) : data containing clean form responses
        """
        if not os.path.exists('barrierReferralData.csv'):
            data = self.updateData()
            logging.debug(f'Updated the data from API.')
        else:
            data = pd.read_csv('barrierReferralData.csv')
            logging.debug(f'Loaded the data from CSV.')

        return data

    def _callAPI(self):
        """
        This method makes an API call to Jotform and returns a JSON object.
        Args:
            None
        Returns:
            data (JSON object) : data containing the response from API request
        """
        api_key = API_KEY
        form_ID = FORM_ID
        limit = 1000

        api_url_submissions = f'https://hipaa-api.jotform.com/form/{form_ID}/submissions?apiKey={api_key}&limit={limit}'


        # Make a GET request to the API
        response = requests.get(api_url_submissions)

        # Check the response status code
        if response.status_code == 200:
            # If the status code is 200, the request was successful
            data = response.json()  # Assuming the API returns JSON data
            logging.debug(f"Succesfully retrieved data. Status code: {response.status_code}")
        else:
            # If the status code is not 200, there was an error
            logging.debug(f"Failed to retrieve data. Status code: {response.status_code}")

        return data
    
    def _createIndexFieldKey(self, data):
        """
        This method creates the self.index_field_key to reference which jotform fields
        match up to which numeric keys. This allows dynamic parsing.

        Args:
            data (dict): dict response from API: BarrierReferralData().response or self.response
        Returns:    
            dict: containing jotform_fields_i: string_integer key-value pairs

        """
        self.index_field_key = {}
        for i in list(data['content'][0]['answers'].keys()):
            json_object = data['content'][0]['answers'][i]['text']
            if json_object in JOTFORM_FIELDS:
                self.index_field_key[f"{json_object.replace(' ', '_').lower()}_i"] = i
        return self.index_field_key
    
    def info(self):
        """
        This method returns meta data on form/API and loads it into the self.meta attribute. The meta
        data includes API limit left, total active entries, and the keys of self.response (json object)
        Args:
            None
        Returns:
            dict : dictionary containing meta data
        """
        data = self.response
        info = {}
        info['limit_left'] = data['limit-left']
        info['json_keys'] = data.keys()

        active_entries = 0
        for entry in data['content']:
            if entry['status'] == 'ACTIVE':
                active_entries += 1
            
        info['active_entries'] = active_entries
        return info
    
    def updateData(self):
        """
        This method processes the JSON object and returns a pandas dataframe and updates the 
        meta, data, barrierData and response attributes when called.
        Args:
            None
        Returns:
            df (pandas.dataframe) : data containing clean form responses
        """
        # call jotform API
        self.response = self._callAPI()
        data = self.response
        self.index_field_key = self._createIndexFieldKey(data)

        # update meta attribute
        self.meta = self.info()

        # column names of csv data
        csv_data = [['date', 'submission_type', 'age', 'sex', 'ethnicity', 'barrier_description', 'barrier_list', 
                     'barrier_cause', 'barrier_solution', 'solution_path', 'referring_org', 
                     'referring_staff', 'staff_email', 'staff_phone','family_contact', 'family_address', 
                     'family_phone', 'family_email','zipcode']]
        
        # iterate through json and format/clean data
        for i in range(len(data['content'])):
            if data['content'][i]['status'] == 'ACTIVE':
                # form_i is the JSON object object containg all data of form i
                form_i = data['content'][i]['answers']

                # submission type
                submission_type = form_i[self.index_field_key['submission_type_i']].get('answer', pd.NA)

                # date
                date_referred = form_i[self.index_field_key['date_i']].get('prettyFormat', pd.NA)
                logging.debug(f'Added date : {date_referred}', )

                # parse organization data
                referring_org, referring_staff, staff_email, staff_phone = self._parseReferrringOrg(i, date_referred)

                # parse family data
                family_contact, family_address, family_phone, family_email = self._parseFamily(i, date_referred)

                # parse barrier log data
                barrier_description, barrier_list, barrier_cause, barrier_solution, solution_path = self._parseBarrierLog(i, date_referred)

                # parse demographic data
                zipcode, age, sex, ethnicity = self._parseDemographics(i, date_referred)

                # extract zipcodes from family address
                if pd.isna(zipcode) == True and pd.isna(family_address) == False:
                    # zipcode general pattern
                    pattern = r'^\d{5}(?:-\d{4})?$'
                    family_address_zipcode = family_address[-5:]
                    # does the extracted zipcode match the pattern?
                    if bool(re.match(pattern, family_address_zipcode)):
                        zipcode = family_address_zipcode
                    # if not, look for any string that matches the 9**** pattern in the address
                    else: 
                      # zipcode pattern with start num as 9
                      pattern = r'\b9\d{4}(?:-\d{4})?\b'
                      match = re.search(pattern, family_address)
                      zipcode = match.group()

                
                # create tuple for data
                row = [date_referred, submission_type, age, sex, ethnicity, barrier_description, barrier_list, 
                       barrier_cause, barrier_solution, solution_path, referring_org, 
                       referring_staff, staff_email, staff_phone, family_contact, family_address, 
                       family_phone, family_email, zipcode]
                csv_data.append(row)

        # create pandas dataframe from list of tuples
        df = pd.DataFrame(csv_data[1:], columns=csv_data[0])

        df['submission_type'] = self._formatSubmissionTypeCol(df['submission_type'])

        # write df to csv file
        df.to_csv('barrierReferralData.csv', index=False) 

        # update self.data and self.barrierData attributes
        self.data = df
        self.barriers = self.barrierData()

        logging.debug(f'Updated the data from API.')

        return df 
    
    def barrierData(self):
        """
        Returns the dataframe without any PHI. Barrier data only.
        Args:
            None
        Returns:
            df (pandas.dataframe) : barrier only data in pd.dataframe
        """
        return self.data.loc[:, ['date', 'age', 'sex', 'ethnicity', 'zipcode', 'barrier_description', 'barrier_list', 'barrier_solution', 'solution_path']]
    
    def topValues(self, col : str, i : int):
        """
        Returns the top i occurences of values in a column.
        Args:
            col (str) : column of interest to make a single list of values from ['barrier_list', 'solution_path']
            i (int) : how many of the top i values to return
        Returns:
            pandas.Series : top i occuring values in ['barrier_list', 'solution_path']
        """
        df = self.barriers
        return pd.Series(self._masterList(col)).value_counts().head(int(i))
    
    def latestDate(self):
        """
        This method returns the latest date in 
        the data in the form (mm-dd-yyyy).
        Args:
            None
        Returns:
            date (string) : date of the latest date in data (mm-dd-yyyy)
        """
        return self.data['date'].sort_values(ascending=False)[0]
    
    def _masterList(self, col : str):
        """
        Reads in a column from a dataframe and returns a combined list. The col choices are 'barrier_list'
        or 'solution_path' since they are the only multiple choices.
        Args:
            col (str) : column of interest to make a single list of values from ['barrier_list', 'solution_path']
        Returns:
            master_list (list) : single list of all input values
        """ 
        df = self.barriers

        master_list = []
        for row in df[col]:
            if pd.isna(row) == False:
                master_list.extend(row.split(';'))
        return master_list
            
    def _parseAddress(self, i : int):
        """
        This helper function parses the address from JSON response data. Does not validate
        the addresses themselves.
        Args:
            i (int) : index i corresponding to the form index in the for loop of updateData()
        Returns:
            cleaned_address (string) : string containing cleaned/parsed address 
        """
        data = self.response

        # form_i is the JSON object object containg all data of form i
        form_i = data['content'][i]['answers']

        # address text
        address_text = form_i[self.index_field_key['family_contact_address_i']].get('prettyFormat', pd.NA)

        if pd.isna(address_text) == False:
            # define a regex pattern to remove unwanted text
            pattern = re.compile(r'(City:|State|Province:|Postal|Zip\s*Code:|Street\s*Address:|Address\s*Line\s*2:|<br>|/)')

            # use re.sub to replace the matched pattern with an empty string
            cleaned_address = re.sub(pattern, ' ', address_text).strip()

            # replace consecutive spaces with a single space
            cleaned_address = re.sub(r'\s+', ' ', cleaned_address)

            return cleaned_address
        else:
            return address_text
        
    def _parseReferrringOrg(self, i : int, date_referred : str):
        """
        This helper function parses the referring org name, staff name,
        staff email, and staff phone number.
        Args:
            i (int) : integer index corresponding to form item in for loop of updateData()
            date_referred : date referred that corresponds to form i's referral date
        Returns:
            tuple : tuple containing strings from target data 
        """
        data = self.response

        # form_i is the JSON object object containg all data of form i
        form_i = data['content'][i]['answers']

        # org
        referring_org = form_i[self.index_field_key['referring_organization_i']].get('answer', pd.NA)
        logging.debug(f'Added org : {date_referred}')

        # referring staff
        referring_staff = form_i[self.index_field_key['referring_staff_name_i']].get('prettyFormat', pd.NA)
        logging.debug(f'Added staff : {date_referred}')
        

        # referring staff email
        staff_email = form_i[self.index_field_key['referring_staff_email_i']].get('answer', pd.NA)
        logging.debug(f'Added staff email : {date_referred}')

        # referring staff number
        staff_phone = form_i[self.index_field_key['referring_staff_phone_number_i']].get('answer', {}).get('full', pd.NA)
        logging.debug(f'Added staff from form : {date_referred}')

        return referring_org, referring_staff, staff_email, staff_phone
    
    def _parseFamily(self, i : int, date_referred : str):
        """
        This helper function parses the family data.
        Args:
            i (int) : integer index corresponding to form item in for loop of updateData()
            date_referred : date referred that corresponds to form i's referral date
        Returns:
            tuple : tuple containing strings from target data
        """
        data = self.response

        # form_i is the JSON object object containg all data of form i
        form_i = data['content'][i]['answers']

         # family contact
        family_contact = form_i[self.index_field_key['family_contact_name_i']].get('prettyFormat', pd.NA)
        logging.debug(f'Added family contacat from form : {date_referred}')

        # address
        family_address = self._parseAddress(i)
        logging.debug(f'Added address from form : {date_referred}')

        # family phone
        family_phone = form_i[self.index_field_key['family_contact_phone_number_i']].get('prettyFormat', pd.NA)
        logging.debug(f'Added family phone from form : {date_referred}')

        # family contact email
        family_email = form_i[self.index_field_key['family_contact_email_i']].get('answer', pd.NA)
        logging.debug(f'Added family email from form : {date_referred}')

        return family_contact, family_address, family_phone, family_email
    
    def _parseBarrierLog(self, i : int, date_referred : str):
        """
        This helper function parses the barrier log data.
        Args:
            i (int) : integer index corresponding to form item in for loop of updateData()
            date_referred : date referred that corresponds to form i's referral date
        Returns:
            tuple : tuple containing strings or lists from target data 
        """
        data = self.response

        # form_i is the JSON object object containg all data of form i
        form_i = data['content'][i]['answers']

         # barrier memo
        barrier_description = form_i[self.index_field_key['barrier_description_i']].get('answer', pd.NA)
        logging.debug(f'Added barrier memo from form : {date_referred}')

        # barrier list 
        barrier_list = form_i[self.index_field_key['barriers_i']].get('prettyFormat', pd.NA)
        logging.debug(f'Added barrier list item from form : {date_referred}')

        # cause to barrier
        barrier_cause = form_i[self.index_field_key['cause_of_barrier_(optional)_i']].get('answer', pd.NA)
        logging.debug(f'Added cause to barrier from form : {date_referred}')

        # solution to barrier
        barrier_solution = form_i[self.index_field_key['solution_to_barrier_(optional)_i']].get('answer', pd.NA)
        logging.debug(f'Added solution to barrier from form : {date_referred}')

        # solution pathway 
        solution_path = form_i[self.index_field_key['solution_pathway_to_barrier_(optional)_i']].get('prettyFormat', pd.NA)
        logging.debug(f'Added solution pathway list item from form : {date_referred}')

        return barrier_description, barrier_list, barrier_cause, barrier_solution, solution_path
    
    def _parseDemographics(self, i : int, date_referred : str):
        """
        This helper function parses the demographic (Zipcode/Sex/Ethnicity) from JSON response data. 
        Args:
            i (int) : index i corresponding to the form index in the for loop of updateData()
            date_referred : date referred that corresponds to form i's referral date
        Returns:
            zipcode, age, sex, ethnicity (tuple) : tuple containing strings or lists from target data
        """
        data = self.response

         # form_i is the JSON object object containg all data of form i
        form_i = data['content'][i]['answers']

         # zipcode
        zipcode = form_i[self.index_field_key['zipcode_i']].get('answer', {}).get('postal', pd.NA)
        logging.debug(f'Added zipcode from form : {date_referred}')

        # age
        age = form_i[self.index_field_key['age_i']].get('answer', pd.NA)
        logging.debug(f'Added age from form : {date_referred}')

        # sex  
        if 'prettyFormat' in list(form_i[self.index_field_key['sex_i']].keys()):
            sex = form_i[self.index_field_key['sex_i']].get('answer', {}).get('other', pd.NA)
        else:
            sex = form_i[self.index_field_key['sex_i']].get('answer', pd.NA)
        logging.debug(f'Added sex from form : {date_referred}')

        # ethnicity
        if 'prettyFormat' in list(form_i[self.index_field_key['ethnicity_i']].keys()):
            ethnicity = form_i[self.index_field_key['ethnicity_i']].get('answer', {}).get('other', pd.NA)
        else:
            ethnicity = form_i[self.index_field_key['ethnicity_i']].get('answer', '')
        logging.debug(f'Added ethnicity from form : {date_referred}')

        return zipcode, age, sex, ethnicity
    
    def _formatSubmissionTypeCol(self, submission_type_col: pd.Series):
        """
        Asserts/formats the three submission types: ['Barrier Log', 'Self-Referral', 'Organization Referral]

        Args:
            submission_type_col: column in self.data containing submission type
        Returns:
            (pd.Series) submission_type_col w/ appropriate categories
        """
        correct_values = ['Barrier Log', 'Self-Referral', 'Organization Referral']

        # Mapping dictionary for replacement
        referral_mapping = {
            'Barrier Log Only (non-referral)': 'Barrier Log'
        }

        # Replace values based on mapping
        mapped = list(submission_type_col.replace(referral_mapping))

        return pd.Series([x if x in correct_values else 'Self-Referral' for x in mapped])


