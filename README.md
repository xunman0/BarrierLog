# Background
- Families in Orange County with children having IDD/MH face an overwhelming amount of barriers to resources and support access
- Despite expressed challenges, healthcare leadership has dismissed the need for significant system changes
- The Advocacy for People with Disabilities project involves 30+ families sharing experiences, identifying barriers, and undergoing advocacy training
- The first phase involved collecting testimonies, resulting in a comprehensive list of identified barriers from their lived experiences
- This initiative aims to empower families and provider organizations to advocate for policy change by creating a "first-ever" dataset that reflects the experiences of families in
a quantifiable way while also referring families to our advocacy group

# Goal
- Begin to identify and understand the barriers of the target population
- Create a dataset than can be presented to OC leadership to acknowledge and expose the reality that their community is facing
- Track/analyze data for future research and use

# Barrier Log Data
barrierReferralData.py:
- Contains the BarrierReferralData class which makes a call to the Jotform API, downloads the data, parses it, and stores the data in a pandas dataframe. It includes helper functions to parse the data and class methods that aid in analysis, updating data, and retreiving meta data on the API/JSON response.

# Streamlit App
app.py: 
- Contains the Plotly plots and logic for Streamlit App

Note: Jotform secrets are stored in Streamlit's secure deployment environment within a .toml file. 

[Barrier Log Link](https://form.jotform.com/240215836883158)

Jotform Account Expires July 2024 (application functionality will depend on this).
