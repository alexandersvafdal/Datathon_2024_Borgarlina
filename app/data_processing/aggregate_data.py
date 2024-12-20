import csv
from data_processing.age_distribution_by_id import get_age_distribution
from data_processing.get_smallAreaInfo import get_smallAreas
from data_processing.get_density import get_density
from data_processing.income_decile_by_id import get_income_decile
import os
import pandas as pd
import geopandas as gpd


def get_feature_df():
    '''
        # TODO
    '''

    # Specify file paths here
    csv_ibuafjoldi = os.path.join('given_data', 'ibuafjoldi.csv')
    csv_tekjutiundir = os.path.join('given_data', 'tekjutiundir.csv')
    json_ibuafjoldi = os.path.join('given_data', 'smasvaedi_2021.json')

    smallareas = gpd.read_file("given_data/smasvaedi_2021.json")

    # Small area id: id of the small area
    # Density: current density of the small area
    # Income distribution: the distribution of income in the small area per year (dictionary, keys: years, values: income distribution [buckets])
    # Age distribution: distibution of age in the small area (age buckets of 5 years starting at 0-4)
    # Geometry: the lat and long coordinates for the small area polygon
    # Projected dwellings: 
    columns = ["smallAreaId", "density", "income_distribution_per_year", "age_distribution", "geometry", "projected_dwellings"]

    # get list of smsv, each represented as {"id": smsv_id, "geometry": [(long, lat), ...]}
    smsv_id_geom = get_smallAreas()
    smsv_ids = [smsv["id"] for smsv in smsv_id_geom]  # list of smsv ids

    # for each smsv_id get the age distribution for several years if required
    years = [2023, 2024]  # Example years for age distribution
    age_distribution = get_age_distribution(years, smsv_ids, csv_ibuafjoldi)  # Dict with age data

    # for each smsv_id get the income distribution (distributed in deciles) for several years if required
    years = [2023, 2024]  # Example years for age distribution
    income_distribution = get_income_decile(years, smsv_ids, csv_tekjutiundir)  # Dict with income data

    # Populate pandas dataframe
    data = []
    for smsv in smsv_id_geom:
        smsv_id = smsv["id"]
        geometry = smsv["geometry"]
        
        # Calculate total population for density calculation
        population = sum(age_distribution.get(smsv_id, {}).get(2024, {}).values())
        
        # Calculate density
        try:
            density = get_density(geometry, population)
        except ValueError as e:
            print(f"Density calculation failed for {smsv_id}: {e}")
            density = None

        # Age distribution
        age_dist = age_distribution.get(smsv_id, {})

        # Income distribution
        income_dist = income_distribution.get(smsv_id, {})
        # Add row to data
        data.append({
            "smallAreaId": smsv_id,
            "density": density,
            "income_distribution_per_year": income_dist,
            "age_distribution": age_dist,
            "geometry": geometry,
            "projected_dwellings": None  # Placeholder for now
        })

    # Convert to Pandas DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Display or save the DataFrame
    # print(df.head())
    # df.to_csv('output.csv', index=False, encoding='utf-8')  # Save to CSV

    return df