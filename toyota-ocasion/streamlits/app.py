import os
import sqlite3

import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

# Set wider width for the whole app
st.set_page_config(layout="wide")

# Assuming you have a function to load your dataset


@st.cache_data
def load_data():

    data_path = os.path.join('data', 'coches.db')

    # create connection to sqlite db
    conn = sqlite3.connect(data_path)

    # Read sqlite db file into a DataFrame
    df = pd.read_sql_query("SELECT * FROM coches", conn)
    return df


# Load the dataset
df = load_data()

# fill car_registration_year from car_registration_date
df['car_registration_year'] = pd.to_datetime(
    df['car_registration_date']
).dt.year

# create mapping dict of cities to dealer_locations
cities_to_locations = {
    c: l for c, l in df[['dealer_city', 'dealer_location']].drop_duplicates().dropna(how='any').values
}

# fill empty dealer_location with city
df['dealer_location'] = df['dealer_location'].fillna(
    df['dealer_city'].map(cities_to_locations)
)

# Identify columns with low cardinality
low_cardinality_cols = [col for col in df.columns if
                        (df[col].nunique() > 1) and
                        (df[col].nunique() < 10)]
# low_cardinality_cols = low_cardinality_cols
df[low_cardinality_cols] = df[low_cardinality_cols].fillna("Unknown")

# Sidebar filters
st.sidebar.header('Filters')

filters = {}

# add a filter for car_price as
filters['car_price'] = st.sidebar.slider(
    'Select car_price range',
    df['car_price'].min(), df['car_price'].max(),
    (df['car_price'].min(), df['car_price'].max())
)
# add a filter for car_mileage
filters['car_mileage'] = st.sidebar.slider(
    'Select car_mileage range',
    df['car_mileage'].min(), df['car_mileage'].max(),
    (df['car_mileage'].min(), df['car_mileage'].max())
)

# add some custom cols not as low cardinality
desired_filters = ['car_brand', 'dealer_location',]
for col in desired_filters:
    filters[col] = st.sidebar.multiselect(f'Select {col}',
                                          options=df[col].unique(),
                                          default=df[col].unique())

# add all low cardinality cols to the sidebar
for col in low_cardinality_cols:
    filters[col] = st.sidebar.multiselect(f'Select {col}',
                                          options=df[col].unique(),
                                          default=df[col].unique())

# Function to filter data based on sidebar filters
@st.cache_data
def filter_data(df, filters):
    # Filter data based on sidebar filters
    filtered_df = df.copy()

    filtered_df = filtered_df[
        (filtered_df['car_price'] >= filters['car_price'][0]) &
        (filtered_df['car_price'] <= filters['car_price'][1])
    ]

    filtered_df = filtered_df[
        (filtered_df['car_mileage'] >= filters['car_mileage'][0]) &
        (filtered_df['car_mileage'] <= filters['car_mileage'][1])
    ]

    for col, values in filters.items():
        if col in ['car_price', 'car_mileage']:
            continue
        print("Filtering by column: ", col,
              " kept with df shape of: ", filtered_df.shape)
        filtered_df = filtered_df[filtered_df[col].isin(values)]

    return filtered_df


# Filter the data
filtered_df = filter_data(df, filters)

# Display the number of rows selected
st.header('Number of Rows Selected')
st.metric(label="", value=filtered_df.shape[0])


# Display a table with a sample of 10 random rows
st.header('Sample of 10 Random Rows (String/Object Columns)')
sample_size = 10 if filtered_df.shape[0] > 10 else filtered_df.shape[0]
if st.button('Refresh Sample'):
    sample_df = filtered_df.sample(sample_size)
else:
    print(filtered_df.shape)
    sample_df = filtered_df.sample(sample_size)

string_columns = sample_df.select_dtypes(include=['object']).columns.tolist()
print('car_age_months' in sample_df.columns)
if 'car_age_months' not in string_columns and 'car_age_months' in sample_df.columns:
    string_columns.append('car_age_months')
st.write(sample_df[string_columns], use_container_width=True)


st.header('Scatter Plot: car_mileage vs. car_price')
fig, ax = plt.subplots()
hue_parameter = st.selectbox('Select Hue Parameter',
                             [
                                 'car_brand',
                                 'dealer_location',
                                 'car_package',
                                 'car_gear_box',
                                 'car_pollution_badge',
                                 'car_seats',
                                 'car_sale_status',
                                 'car_history_previous_usage',
                                 'car_model',
                                 'dealer_name',
                                 None
                             ]
                             )
style_parameter = st.selectbox('Select Style Parameter',
                               ['car_fuel',  'car_registration_year', None, ]
                               )

sns.scatterplot(data=filtered_df,
                x='car_mileage', y='car_price',
                hue=hue_parameter,
                style=style_parameter,
                legend='brief',
                ax=ax)
# move legend outside of the plot to the right
# plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
st.pyplot(fig)

# Create columns for side-by-side plots
col1, col2 = st.columns(2)

# Scatter plot
with col1:
    fig, ax = plt.subplots()
    year_counts = filtered_df['car_package'].value_counts()
    title = 'Counts by car packages'
    if year_counts.shape[0] > 20:
        year_counts = year_counts.head(20)
        title = 'Top 20 car packages'
    year_counts.plot(kind='barh', ax=ax)
    st.header(title)
    st.pyplot(fig)

# Horizontal bar plot
with col2:
    st.header('Count of Rows per Year')
    fig, ax = plt.subplots()
    year_counts = filtered_df['car_registration_year'].value_counts()
    year_counts.plot(kind='barh', ax=ax)
    st.pyplot(fig)


# Additional visualizations
# Barh for transmission and fuel
col3, col4 = st.columns(2)
with col3:
    fig, ax = plt.subplots()
    transmission_counts = filtered_df['car_transmission'].value_counts()
    transmission_counts.plot(kind='barh', ax=ax)
    title = 'Counts by car transmission'
    if transmission_counts.shape[0] > 20:
        title = 'Top 20 car transmissions'
        transmission_counts = transmission_counts.head(20)
    st.header(title)    
    st.pyplot(fig)

with col4:
    fig, ax = plt.subplots()
    fuel_counts = filtered_df['car_fuel'].value_counts()
    fuel_counts.plot(kind='barh', ax=ax)
    title = 'Counts by car fuel'
    if fuel_counts.shape[0] > 20:
        title = 'Top 20 car fuels'
        fuel_counts = fuel_counts.head(20)
    st.header(title)
    st.pyplot(fig)

# Barh for interior and bodystyle
col5, col6 = st.columns(2)
with col5:
    fig, ax = plt.subplots()
    interior_counts = filtered_df['car_interior_color'].value_counts()
    interior_counts.plot(kind='barh', ax=ax)
    title = 'Counts by car interior color'
    if interior_counts.shape[0] > 20:
        title = 'Top 20 car interior colors'
        interior_counts = interior_counts.head(20)
    st.pyplot(fig)

with col6:
    st.header('Count of Rows per Exterior Color')
    fig, ax = plt.subplots()
    exterior_counts = filtered_df['car_exterior_color'].value_counts()
    exterior_counts.plot(kind='barh', ax=ax)
    title = 'Counts by car exterior color'
    if exterior_counts.shape[0] > 20:
        title = 'Top 20 car exterior colors'
        exterior_counts = exterior_counts.head(20)
    st.pyplot(fig)

# Barh for emissionClass and remainingWarrantyWholeYears
col7, col8 = st.columns(2)
with col7:
    st.header('Count of Rows per Emissions Class')
    fig, ax = plt.subplots()
    emission_class_counts = filtered_df['car_emissions_class'].value_counts()
    emission_class_counts.plot(kind='barh', ax=ax)
    st.pyplot(fig)

with col8:
    title = 'Count of Rows per Remaining Warranty Whole Years'
    fig, ax = plt.subplots()
    warranty_counts = filtered_df['car_remaining_warranty'].value_counts()
    if warranty_counts.shape[0] > 10:
        warranty_counts = warranty_counts.head(10)
        title = 'Top 10 Remaining Warranty Whole Years'

    st.header(title)
    warranty_counts.plot(kind='barh', ax=ax)
    st.pyplot(fig)


# Boxplots grouped by model_name
st.header('Boxplots: car_price vs. car_model for each model name')
car_model_names = filtered_df['car_model_name'].value_counts()\
                    .head(10).index.values

for model in car_model_names:
    for engine in filtered_df['car_engine'].dropna().unique():
        model_df = filtered_df[(filtered_df['car_model_name'] == model)
                               & (filtered_df['car_engine'] == engine)]

        print(f"Model: {model} - Engine: {engine} - Shape: {model_df.shape}")

        if model_df.shape[0] < 20:
            print(f"Skipping {model} - {engine} boxplot")
            continue

        st.subheader(f'Model: {model} - Engine: {engine}')
        fig, ax = plt.subplots()
        sns.violinplot(data=model_df,
                       x='car_model', y='car_price',
                       ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

st.title("Pairplot car_price vs. car_mileage")
fig = sns.pairplot(filtered_df[['car_price', 'car_mileage']],
                   #    hue="registration"
                   )
st.pyplot(fig)
