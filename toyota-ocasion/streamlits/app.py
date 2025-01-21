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

    data_path = st.secrets["DB_PATH"] or os.path.join('data', 'coches.db')

    # create connection to sqlite db
    conn = sqlite3.connect(data_path)

    # Read sqlite db file into a DataFrame
    df = pd.read_sql_query("SELECT * FROM coches", conn)

    # drop full empty columns
    df = df.dropna(axis=1, how='all')

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

    # fix dealer_location values - remove accents
    df['dealer_location'] = df['dealer_location'].str.upper()\
        .str.normalize('NFKD')

    return df


# Load the dataset
df = load_data()

# Identify columns with low cardinality
low_cardinality_cols = [col for col in df.columns if
                        (df[col].nunique() > 1) and
                        (df[col].nunique() < 10)]
# low_cardinality_cols = low_cardinality_cols
df[low_cardinality_cols] = df[low_cardinality_cols].fillna("Unknown")


#
# Sidebar filters
#
st.sidebar.header('Filters')

filters = {}

# add a filter for car_price as
filters['car_price'] = st.sidebar.slider(
    'Select car price range:',
    df['car_price'].min(), df['car_price'].max(),
    (df['car_price'].min(), df['car_price'].max())
)
# add a filter for car_mileage
filters['car_mileage'] = st.sidebar.slider(
    'Select car mileage range:',
    df['car_mileage'].min(), df['car_mileage'].max(),
    (df['car_mileage'].min(), df['car_mileage'].max())
)

# add some custom cols not as low cardinality
desired_filters = ['car_brand', 'dealer_location',]
for col in desired_filters:
    col_name = col.replace('_', ' ')
    filters[col] = st.sidebar.multiselect(f'Select {col_name}:',
                                          options=df[col].unique(),
                                          default=df[col].unique())

# add all low cardinality cols to the sidebar
for col in low_cardinality_cols:
    col_name = col.replace('_', ' ')
    filters[col] = st.sidebar.multiselect(f'Select {col_name}:',
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
        filtered_df = filtered_df[filtered_df[col].isin(values)]

    return filtered_df


# Filter the data
filtered_df = filter_data(df, filters)

############################################
# Dashboard tabs
############################################
tab1, tab2, tab3, tab4 = st.tabs(
    ["Geo & Table", "Counts", "Price Ranges", "Price vs Mileage"])

############################################
# Charts and tables
############################################

with tab1:

    df_geo = filtered_df\
        .dropna(how='any', subset=['dealer_geo_lat', 'dealer_geo_lon'])

    st.header('Geographical distribution of dealers')
    fig, ax = plt.subplots()
    st.map(df_geo,
           latitude="dealer_geo_lat",
           longitude="dealer_geo_lon",
           )

    # Display the number of rows selected
    st.header('Number of cars selected')
    st.metric(label='', value=df_geo.shape[0])

    # Display a table with a sample of 10 random rows
    st.header('Sample of cars selected')
    sample_size = 10 if df_geo.shape[0] > 10 else df_geo.shape[0]
    if st.button('Refresh Sample'):
        sample_df = df_geo.sample(sample_size)
    else:
        sample_df = df_geo.sample(sample_size)

    string_columns = sample_df.select_dtypes(include=['object'])\
        .columns.tolist()
    if 'car_age_months' not in string_columns and 'car_age_months' in sample_df.columns:
        string_columns.append('car_age_months')
    st.write(sample_df[string_columns], use_container_width=True)

    st.title("Price vs Province")
    fig, ax = plt.subplots()
    sns.barplot(
        data=df_geo[
            ['dealer_location', 'car_price', ]
        ].sort_values(by='dealer_location'),
        x='car_price',
        y='dealer_location',
        ax=ax
    )
    plt.yticks(fontsize=6, rotation=15)
    plt.xticks(fontsize=8, rotation=45)
    plt.xlabel('Price Range (€)')
    plt.ylabel('')
    st.pyplot(fig)

    st.title("Price vs Catalogue Price")
    fig, ax = plt.subplots()
    sns.histplot(
        data=df_geo[['car_price', 'car_catalogue_price']],
        x='car_price',
        y='car_catalogue_price',
        ax=ax
    )
    plt.xticks(fontsize=8, rotation=45)
    plt.xlabel('')
    plt.ylabel('Price Range (€)')
    st.pyplot(fig)

with tab2:
    # Display the number of rows selected
    st.header('Number of cars selected')
    st.metric(label='', value=filtered_df.shape[0])

    # Create columns for side-by-side plots
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(10, 8))
        year_counts = filtered_df['car_registration_year'].value_counts()
        year_counts.index = year_counts.index.astype(int)
        title = 'Car Registrations per Year'
        if year_counts.shape[0] > 20:
            year_counts = year_counts.head(20)
            title = 'Top 20 Registration Years'
        st.header(title)
        sns.barplot(year_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_registration_year': 'Registration Year'})
                    .rename(columns={'count': 'Counts'}),
                    x="Registration Year",
                    y="Counts",
                    palette="viridis",
                    hue="Registration Year",
                    legend=False)
        st.pyplot(fig)

    with col2:

        fig, ax = plt.subplots(figsize=(6, 8))
        package_counts = filtered_df['car_package'].value_counts()
        title = 'Car packages'
        if package_counts.shape[0] > 20:
            package_counts = package_counts.head(20)
            title = 'Top 20 car packages'
        st.header(title)
        sns.barplot(package_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_package': 'Car Package'})
                    .rename(columns={'count': 'Counts'}),
                    x="Counts",
                    y="Car Package",
                    palette="viridis",
                    hue="Car Package",
                    legend=False)
        st.pyplot(fig)

    # Additional visualizations
    # Barh for transmission and fuel
    col3, col4 = st.columns(2)
    with col3:
        fig, ax = plt.subplots()
        transmission_counts = filtered_df['car_transmission'].value_counts()
        title = 'Car transmissions'
        if transmission_counts.shape[0] > 20:
            title = 'Top 20 Car Transmissions'
            transmission_counts = transmission_counts.head(20)
        st.header(title)
        sns.barplot(transmission_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_transmission': 'Car Transmission'})
                    .rename(columns={'count': 'Counts'}),
                    x="Counts",
                    y="Car Transmission",
                    palette="viridis",
                    hue="Car Transmission",
                    legend=False)
        st.pyplot(fig)

    with col4:
        fig, ax = plt.subplots()
        fuel_counts = filtered_df['car_fuel'].value_counts()
        title = 'Car fuel types'
        if fuel_counts.shape[0] > 20:
            title = 'Top 20 car fuels'
            fuel_counts = fuel_counts.head(20)
        st.header(title)
        sns.barplot(fuel_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_fuel': 'Car Fuel'})
                    .rename(columns={'count': 'Counts'}),
                    x="Counts",
                    y="Car Fuel",
                    palette="viridis",
                    hue="Car Fuel",
                    legend=False)
        st.pyplot(fig)

    # Barh for interior and bodystyle
    col5, col6 = st.columns(2)
    with col5:
        fig, ax = plt.subplots(figsize=(8, 8))
        interior_counts = filtered_df['car_interior_color'].value_counts()
        title = 'Car interior colors'
        if interior_counts.shape[0] > 20:
            title = 'Top 20 car interior colors'
            interior_counts = interior_counts.head(20)
        st.header(title)
        sns.barplot(interior_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_interior_color': 'Interior Color'})
                    .rename(columns={'count': 'Counts'}),
                    x="Counts",
                    y="Interior Color",
                    palette="viridis",
                    hue="Interior Color",
                    legend=False)
        st.pyplot(fig)

    with col6:
        fig, ax = plt.subplots(figsize=(8, 8))
        exterior_counts = filtered_df['car_exterior_color'].value_counts()
        title = 'Car exterior colors'
        if exterior_counts.shape[0] > 20:
            title = 'Top 20 car exterior colors'
            exterior_counts = exterior_counts.head(20)
        st.header(title)

        sns.barplot(exterior_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_exterior_color': 'Exterior Color'})
                    .rename(columns={'count': 'Counts'}),
                    x="Counts",
                    y="Exterior Color",
                    palette="viridis",
                    hue="Exterior Color",
                    legend=False)
        st.pyplot(fig)

    # Barh for emissionClass and remainingWarrantyWholeYears
    col7, col8 = st.columns(2)
    with col7:
        st.header('Car Emissions Classes')
        fig, ax = plt.subplots()
        emission_class_counts = filtered_df['car_emissions_class']\
            .value_counts()
        sns.barplot(emission_class_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_emissions_class': 'Emissions Class'})
                    .rename(columns={'count': 'Counts'}),
                    x="Counts",
                    y="Emissions Class",
                    palette="viridis",
                    hue="Emissions Class",
                    legend=False)
        st.pyplot(fig)

    with col8:
        title = 'Car Remaining Warranty Whole Years'
        fig, ax = plt.subplots()
        warranty_counts = filtered_df['car_remaining_warranty'].value_counts()
        if warranty_counts.shape[0] > 10:
            warranty_counts = warranty_counts.head(10)
            title = 'Top 10 Car Remaining Warranty Whole Years'

        st.header(title)
        sns.barplot(warranty_counts
                    .reset_index(drop=False)
                    .rename(columns={'car_remaining_warranty': 'Remaining Warranty'})
                    .rename(columns={'count': 'Counts'}),
                    x="Counts",
                    y="Remaining Warranty",
                    palette="viridis",
                    hue="Remaining Warranty",
                    legend=False)
        st.pyplot(fig)


# tab3
with tab3:
    st.header('Select a car brand:')

    # select a car brand, by default 'Toyota'
    car_brand = st.selectbox('',
                             filtered_df['car_brand'].unique(),
                             index=0)
    df3 = filtered_df[filtered_df['car_brand'] == car_brand]
    df3.sort_values(by=['car_brand', 'car_model', 'car_package'], inplace=True)

    # Display the number of rows selected
    st.header('Number of cars selected')
    st.metric(label='', value=df3.shape[0])

    # Boxplots grouped by model_name
    st.header('Car packages\'s prices ranges by car model')
    car_model_names = df3['car_model'].value_counts()\
        .head(10).index.values

    for model in car_model_names:
        if df3.shape[0] < 10:
            st.warning(f"Skipping {model} boxplot due to very few data points")
            continue

        top_car_packages = df3[df3['car_model'] ==
                               model]['car_package'].value_counts().head(5)
        top_car_packages = top_car_packages[top_car_packages > 1]
        top_car_packages = top_car_packages.index.values

        model_df = df3[
            (df3['car_model'] == model) &
            (df3['car_package'].isin(top_car_packages))
        ]
        if model_df.shape[0] < 3:
            st.warning(f"Skipping {model} boxplot due to very few data points")
            continue

        st.subheader(f'Model: {model}')
        fig, ax = plt.subplots()
        sns.violinplot(data=model_df,
                       x='car_package', y='car_price',
                       hue='car_package',
                       ax=ax)
        plt.xticks(fontsize=8, rotation=45)
        plt.xlabel('')
        plt.ylabel('Price Range (€)')
        st.pyplot(fig)

with tab4:
    # Display the number of rows selected
    st.header('Number of cars selected')
    st.metric(label='', value=filtered_df.shape[0])

    st.header('Mileage vs. Price')
    fig, ax = plt.subplots()
    hue_parameter = st.selectbox('Select Hue Parameter',
                                 [
                                     'car_brand',
                                     'dealer_location',
                                     'car_registration_year',
                                     'car_gear_box',
                                     'car_sale_status',
                                     'car_history_previous_usage',
                                     None
                                 ]
                                 )
    style_parameter = st.selectbox('Select Style Parameter',
                                   ['car_fuel',
                                    'car_pollution_badge',
                                    'car_seats',
                                    'dealer_name',
                                    None, ]
                                   )

    sns.scatterplot(data=filtered_df,
                    x='car_mileage', y='car_price',
                    hue=hue_parameter,
                    style=style_parameter,
                    legend='brief',
                    ax=ax)
    plt.xlabel('Mileage')
    plt.ylabel('Price')
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    st.pyplot(fig)

    st.title("Mileage vs Price")
    fig = sns.pairplot(
        filtered_df[['car_mileage',
                     'car_price',
                     'car_catalogue_price',
                     'car_martket_price',
                     'car_registration_year']],
        hue="car_registration_year")
    st.pyplot(fig)
