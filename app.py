import streamlit as st
import pandas as pd
from barrierReferralData import BarrierReferralData
import plotly.express as px
from uszipcode import SearchEngine
search = SearchEngine()

def display_top_barriers(i: int, col: str = 'barrier_list'):
    """
    Display the top barriers based on the specified column.
    
    Args:
        i (int): Number of top barriers to display.
        col (str): Column name to consider for displaying top barriers.

    Returns:
        None
    """
    top_values = barriers.topValues(col, i)
    st.write(f'##### Top {i} Barriers')
    st.write(top_values)


def zco(x):
    """
    Get the city name from the zip code.

    Args:
        x (int): Zip code.

    Returns:
        str: City name or the zip code if city name is not found.
    """
    try:
        city = search.by_zipcode(x).major_city
        return city 
    except AttributeError:
        return x

def load_csv_data(df):
    """
    Generate a download button to download data as a CSV file.

    Args:
        df (pandas.DataFrame): DataFrame to be converted to CSV.

    Returns:
        None
    """
    @st.cache_data
    def convert_df(df):
       return df.to_csv(index=False).encode('utf-8')
    csv = convert_df(df)
    st.sidebar.download_button(
        "Download Barrier Data",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv'
    )

def display_city_distribution(i: int):
    """
    Display the distribution of cities based on the number of barriers.

    Args:
        i (int): Number of cities to display in the distribution.

    Returns:
        None
    """
    city_counts = barriers.barriers['zipcode'].apply(zco).astype('string').value_counts().reset_index()[:i]
    city_counts.columns = ['zipcode', 'count']
    fig_city = px.bar(city_counts, x='zipcode', y='count',
                    title='City Distribution',
                    labels={'zipcode': 'City', 'count': 'Count'})
    st.plotly_chart(fig_city, use_container_width=True)

def refresh_data():
    """
   Refreshes data and figures.

    Args:
        None

    Returns:
        None
    """
    barriers.updateData()
    st.sidebar.success("Data refreshed successfully.")

# Load data and update if necessary
barriers = BarrierReferralData()
barriers.updateData()

# Top Solution Pathways
top_solution_data = barriers.topValues('solution_path', 10)
fig_solution = px.bar(top_solution_data, x=top_solution_data.index, y=top_solution_data.values,
                      labels={'y': 'Count', 'index': ' '}, 
                      title='Top Solution Pathways')

# Ethnicity Distribution
ethnicity_counts = barriers.barriers['ethnicity'].value_counts().reset_index()
ethnicity_counts.columns = ['ethnicity', 'count']
fig_ethnicity = px.pie(ethnicity_counts, names='ethnicity', values='count',
                       title='Ethnicity Distribution',
                       labels={'ethnicity': 'Ethnicity', 'count': 'Count'},
                       hole=0.3)
fig_ethnicity.update_traces(textinfo='percent+label', pull=[0.1] * len(ethnicity_counts))

# Sex Distribution
sex_counts = barriers.barriers['sex'].value_counts().reset_index()
sex_counts.columns = ['sex', 'count']
fig_sex = px.pie(sex_counts, names='sex', values='count',
                 title='Sex Distribution',
                 labels={'sex': 'Sex', 'count': 'Count'},
                 hole=0.3)
fig_sex.update_traces(textinfo='percent+label', pull=[0.1] * len(sex_counts))

# Age Distribution
age_distribution = barriers.barriers['age'].value_counts().sort_index().reset_index()
age_distribution.columns = ['age', 'count']
fig_age = px.bar(age_distribution, x='age', y='count',
                 title='Age Distribution',
                 labels={'age': 'Age', 'count': 'Count'},
                 hover_data=['age', 'count'],
                 category_orders={"age": list(range(26))})

# Streamlit App
st.title('Barrier Referral Data Analysis')

# Sidebar for user input
i = st.sidebar.number_input("Filter Barrier Count", min_value=1, value=10)
i_city = st.sidebar.number_input("Filter City Count", min_value=1, value=10)

def run_figures():
# Display top values
    display_top_barriers(i)

    st.plotly_chart(fig_ethnicity, use_container_width=True)

    st.plotly_chart(fig_sex, use_container_width=True)

    st.plotly_chart(fig_age, use_container_width=True)

    # Display city distribution
    display_city_distribution(i_city)

    st.plotly_chart(fig_solution, use_container_width=True)

    st.dataframe(barriers.barriers) 

# Refresh button in the sidebar
if st.sidebar.button("Refresh Data"):
    refresh_data()
    run_figures()

run_figures()

# Load button in sidebar
load_csv_data(barriers.barriers)

# Link to Barrier Log
st.sidebar.markdown("[Barrier Log Link](https://form.jotform.com/240215836883158)")