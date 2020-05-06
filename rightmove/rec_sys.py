import json
import os
import time

import numpy as np
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

SECRET_KEY_GOOGLE_MAPS = os.environ.get("SECRET_KEY_GOOGLE_MAPS")
SECRET_KEY_GEOCODING = os.environ.get("SECRET_KEY_GEOCODING")


def call_geocoding_api(address):
    address = address.lower()
    complete_work_address = address + ' london' if 'london' not in address else address
    map_add_coord = {
        'locate': complete_work_address,
        'geoit': 'json',
        'auth': SECRET_KEY_GEOCODING}
    coord_request = requests.post('https://geocode.xyz/', data=map_add_coord)
    coord_json = coord_request.text
    coord_dict = json.loads(coord_json)
    latitude = coord_dict.get('latt')
    longitude = coord_dict.get('longt')
    work_coord = latitude + ',' + longitude
    return work_coord


def call_distance_matrix_api(area, work_address, key_google_maps):
    params = {'origins': area,
              'destinations': work_address,
              'key': key_google_maps,
              'mode': 'transit'}
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    req = requests.get(url, params=params)
    response_json = req.text
    response_dict = json.loads(response_json)
    response_rows = response_dict['rows'][0]
    response_elements = response_rows['elements'][0]
    if response_elements['status'] != 'OK':
        return np.NaN
    else:
        response_duration = response_elements['duration']
        response_duration_text = response_duration['text']
        time_to_work = float(''.join(i for i in response_duration_text if i.isdigit()))
        return time_to_work


def populate_time_to_work(row, map_area_time_to_work):
    return map_area_time_to_work.get(row)


class RecSys:
    def __init__(self, user_vector, df_rightmove):
        start_time = time.time()

        self.user_vector = user_vector
        df_copy = df_rightmove.copy()
        self.df_original = df_copy
        self.df_rightmove = df_copy

        # Sub sample df based on user inputs
        self.df_rightmove = self.df_rightmove[self.df_rightmove['number_bedrooms'] == self.user_vector[0]]
        self.df_rightmove = self.df_rightmove[self.df_rightmove['price'] <= self.user_vector[1]]

        columns_to_keep = ['id', 'number_bedrooms', 'price', 'area', 'address']
        for col in self.df_rightmove.columns:
            if col not in columns_to_keep:
                self.df_rightmove.drop(col, axis=1, inplace=True)
        self.map_area_similarity = {}
        self.list_3_rec_areas = []
        self.list_3_coord_rec_areas = []
        self.list_3_avg_time_work_rec_areas = []

        # Process work address
        work_address = self.user_vector[2]
        work_address = work_address.lower()
        work_address = work_address + ' london' if 'london' not in work_address else work_address

        map_area_time_to_work = {}
        # Calculate time to work by areas (minimise API calls)
        for area in self.df_rightmove['area'].unique():
            # Process area
            area_lower = area.lower()
            area_london = area_lower + ' london' if 'london' not in area_lower else area_lower
            # Add time to work to a dictionary mapping area and time
            time_to_work = call_distance_matrix_api(area_london, work_address, SECRET_KEY_GOOGLE_MAPS)
            map_area_time_to_work[area] = time_to_work

        # Create time to work feature
        self.df_rightmove['time_to_work'] = self.df_rightmove['area'].apply(populate_time_to_work,
                                                                            map_area_time_to_work=map_area_time_to_work)


        # Delete NaN rows
        self.df_rightmove.dropna(inplace=True)

        # Remove entries which have a time to work bigger than user input
        self.df_rightmove = self.df_rightmove[self.df_rightmove['time_to_work'] <= self.user_vector[3]]

        # Delete unwanted cols
        df_wo_id_address_area = self.df_rightmove.copy()
        df_wo_id_address_area.drop(['id', 'address', 'area'], axis=1, inplace=True)
        del self.user_vector[2]

        if self.df_rightmove.shape[0] != 0:

            # Standardise both user vector and home vectors
            scaler = StandardScaler().fit(df_wo_id_address_area.values)
            scaled_home_vectors = scaler.transform(df_wo_id_address_area)
            scaled_user_vector = scaler.transform(np.asarray(self.user_vector).reshape(1, -1))

            # Calculate cosine similarity
            sim_houses_user = cosine_similarity(scaled_home_vectors, scaled_user_vector)

            # Add cosine similarity to homes vector
            self.df_rightmove['similarity'] = sim_houses_user

            # Group by area and calculate avg of similarity by area
            groups = self.df_rightmove.groupby('area')

            for group in groups:
                area = group[0]
                df = group[1]
                avg_sim = df['similarity'].mean()
                self.map_area_similarity[area] = avg_sim

            # Order rec areas descending and create list with 3 best recs
            list_ordered_areas = sorted(self.map_area_similarity, key=self.map_area_similarity.__getitem__, reverse=True)
            self.list_3_rec_areas = list_ordered_areas[0:3]

            # Create list with 3 best recs and with averages of times to work
            for area in self.list_3_rec_areas:
                # Recommended areas coordinates
                coord_area = call_geocoding_api(area)
                self.list_3_coord_rec_areas.append(coord_area)
                # Average times to work of recommended areas
                df_area = self.df_rightmove[self.df_rightmove['area'] == area]
                avg_time_to_work = df_area['time_to_work'].mean()
                self.list_3_avg_time_work_rec_areas.append(avg_time_to_work)

            # For the heatmap we need a dataframe that has diff number bedrooms / diff prices / diff times to work
            list_areas = list(map_area_time_to_work.keys())
            self.df_original = self.df_original[self.df_original['area'].isin(list_areas)]
            self.df_original['time_to_work'] = self.df_original['area'].apply(populate_time_to_work,
                                                                              map_area_time_to_work=map_area_time_to_work)
        else:
            self.list_3_rec_areas = []
            self.list_3_coord_rec_areas = []
            self.list_3_avg_time_work_rec_areas = []

        print('Total time seconds: ', time.time() - start_time)

    def get_rec_areas(self):
        return self.list_3_rec_areas

    def get_rec_areas_coord(self):
        return self.list_3_coord_rec_areas

    def get_rec_areas_time_work(self):
        return self.list_3_avg_time_work_rec_areas

    def get_home_vectors_df(self):
        return self.df_rightmove

    def get_df_heatmap(self):
        return self.df_original


if __name__ == '__main__':
    user_vector = [1, 1000,  'Old St, London', 30]
    df_home_vector = RecSys(user_vector).get_home_vectors_df()
    print(df_home_vector.head())
