# [Hosted Streamlit App](https://barrierlogoc.streamlit.app)
# Background
- Families in Orange County with children having an intellectual or developmental disabilities/mental health (IDD/MH) diagnosis face an overwhelming amount of barriers to resources and support access
- Despite expressed challenges, healthcare leadership has dismissed the need for significant system changes
- The Advocacy for People with Disabilities project involves 30+ families sharing experiences, identifying barriers, and undergoing advocacy training
- The first phase involved collecting testimonies, resulting in a comprehensive list of identified barriers from their lived experiences
- This initiative aims to empower families and provider organizations to advocate for policy change by creating a "first-ever" dataset that reflects the experiences of families in
a quantifiable way while also referring families to our advocacy group

# Data Collection
- Anyone who witnessess an incident of system barriers is encouraged to fill out this [barrier log](st.markdown("[More information and context about this data.](https://form.jotform.com/240215836883158)
- Individuals filling out the log include but are not limited to:
  - Family/Caregivers
  - Social workers
  - Therapists (Behavioral/Speech/Occupational/Physical/Mental)
  - Medical Personnel (Physicians/Nurses/etc)
  - Community Navigators
  - CBO Leaders/Staff
  - RCOC Staff

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

### Note: 
- Jotform credentials/secrets are stored in Streamlit's secure deployment environment within a .toml file.
- Jotform Account Expires July 2024 (application functionality will depend on this).
- This is not academic research nor aims to make statistically significant findings with rigorous methodology
- The main goal of this initiative is for exploration of the lived experiences of OC's community with respect to healthcare barriers and children with IDD/MH 
