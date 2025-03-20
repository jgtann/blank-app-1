import streamlit as st
import pandas as pd
import plotly.express as px
import country_converter as coco

# Load and preprocess data
df = pd.read_csv("Countries_Languages_Continent_Region.csv")

# Split Continental Region into Continent and Region
df[['Continent', 'Region']] = df['Continental Region'].str.extract(r'^([^\(]+)(?:\((.*)\))?$')
df['Continent'] = df['Continent'].str.strip()
df['Region'] = df['Region'].str.strip()

# Function to extract languages from multiple columns
def extract_languages(row):
    langs = []
    columns_to_check = [
        'Main Spoken Languages/Language Groups (with estimated % of first language speakers if over 10% of population)',
        'Languages with official status',
        'Languages with national or regional status'
    ]
    
    for col in columns_to_check:
        if pd.notna(row[col]):
            for lang in row[col].split(', '):
                # Remove percentage information and trim
                clean_lang = lang.split('(')[0].strip()
                if clean_lang:
                    langs.append(clean_lang)
    return list(set(langs))  # Remove duplicates

df['All_Languages'] = df.apply(extract_languages, axis=1)

# Standardize country names for mapping
def standardize_country(name):
    return coco.convert(names=name, to='name_short')

df['Country_Standard'] = df['Country'].apply(standardize_country)

# Streamlit app
st.title("Interactive Country Map Explorer")

# Create filters
selected_continent = st.sidebar.multiselect(
    "Select Continent",
    options=sorted(df['Continent'].unique()),
    default=None
)

available_regions = df[df['Continent'].isin(selected_continent)]['Region'].unique() if selected_continent else []
selected_region = st.sidebar.multiselect(
    "Select Region",
    options=sorted(available_regions),
    default=None
)

# Country filter (based on continent/region selection)
filtered_countries = df
if selected_continent:
    filtered_countries = filtered_countries[filtered_countries['Continent'].isin(selected_continent)]
if selected_region:
    filtered_countries = filtered_countries[filtered_countries['Region'].isin(selected_region)]

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(filtered_countries['Country'].unique()),
    default=None
)

# Language filter (based on current selection)
all_languages = list(set([lang for sublist in filtered_countries['All_Languages'] for lang in sublist]))
selected_languages = st.sidebar.multiselect(
    "Select Languages",
    options=sorted(all_languages),
    default=None
)

# Apply filters
final_df = df
if selected_continent:
    final_df = final_df[final_df['Continent'].isin(selected_continent)]
if selected_region:
    final_df = final_df[final_df['Region'].isin(selected_region)]
if selected_countries:
    final_df = final_df[final_df['Country'].isin(selected_countries)]
if selected_languages:
    final_df = final_df[final_df['All_Languages'].apply(lambda x: any(lang in x for lang in selected_languages))]

# Create map
st.subheader("Interactive Map")
fig = px.choropleth(
    final_df,
    locations="Country_Standard",
    locationmode='country names',
    color="Continent",
    hover_name="Country",
    hover_data=[
        "Population (million) (2005 UN estimates)",
        "No. of native spoken languages",
        "All_Languages"
    ],
    title="Country Distribution Map"
)
st.plotly_chart(fig)

# Show raw data
st.subheader("Filtered Data")
st.dataframe(final_df)