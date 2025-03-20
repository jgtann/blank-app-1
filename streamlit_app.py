import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page layout to wide for better screen utilization
st.set_page_config(layout="wide")

# Safely load dataset
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('Countries_Languages_Continent_Region.csv')
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

data = load_data()

if not data.empty:
    # Streamlit title
    st.title('Interactive Country Map with Filters')

    # Sidebar filters
    continent_filter = st.sidebar.multiselect('Select Continent', options=data['continent'].unique(), default=data['continent'].unique())

    # Cascaded filtering for countries based on continent selection
    available_countries = data[data['continent'].isin(continent_filter)]['country'].unique()
    country_filter = st.sidebar.multiselect('Select Country', options=available_countries, default=[])

    language_filter = st.sidebar.text_input('Search Language')

    # Filter dataset based on selections
    filtered_data = data[data['continent'].isin(continent_filter)]

    if country_filter:
        filtered_data = filtered_data[filtered_data['country'].isin(country_filter)]

    if language_filter:
        filtered_data = filtered_data[filtered_data['main_spoken_languages'].str.contains(language_filter, case=False, na=False)]

    # Prepare hover text explicitly with safe handling of missing data
    filtered_data['hover_text'] = (
        filtered_data['country'].fillna('Country: N/A') + '<br>' +
        'Population (2005): ' + filtered_data['population_million_2005'].fillna('N/A').astype(str) + ' million<br>' +
        'Native Languages: ' + filtered_data['no_native_languages'].fillna('N/A').astype(str) + '<br>' +
        'Main Languages: ' + filtered_data['main_spoken_languages'].fillna('N/A') + '<br>' +
        'Official Languages: ' + filtered_data['languages_official_status'].fillna('N/A') + '<br>' +
        'Regional Languages: ' + filtered_data['languages_national_or_regional_status'].fillna('N/A')
    )

    # Interactive map using Plotly with custom hover text
    fig = px.choropleth(
        filtered_data,
        locations='country',
        locationmode='country names',
        color='continent',
        hover_name=None,
        hover_data={'hover_text': True, 'continent': False},
        title='Countries Highlighted by Filters'
    )

    # Improve hover and visual aesthetics
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color='black',
        hoverlabel=dict(font_size=14),
        hovertemplate='%{customdata[0]}<extra></extra>'
    )
    fig.update_geos(fitbounds="locations", visible=False)

    # Adjust the map layout to fully utilize the available width and height
    fig.update_layout(
        autosize=True,
        margin={"r":0, "t":40, "l":0, "b":0},
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth')
    )

    # Display map in Streamlit
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("The dataset is empty or failed to load. Please check your file.")