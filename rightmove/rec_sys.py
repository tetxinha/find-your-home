import json
import os
import time

import numpy as np
import requests
from load import Load
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

SECRET_KEY_CITYMAPPER = os.environ.get("SECRET_KEY_CITYMAPPER")
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


def call_citymapper_api(row, work_coord, key_citymapper):
    map_time_center = {'startcoord': row,
                       'endcoord': work_coord,
                       'key': key_citymapper}
    time_to_work_req = requests.get('https://developer.citymapper.com/api/1/traveltime/', map_time_center)
    time_to_work_response = time_to_work_req.json()
    time_to_work = time_to_work_response.get('travel_time_minutes')
    return time_to_work


class RecSys:
    def __init__(self, user_vector):
        self.user_vector = user_vector
        self.df_home_vectors = Load('home_vectors').read_db()
        print(self.df_home_vectors.head())
        print(self.df_home_vectors.shape[0])
        self.map_area_similarity = {}
        self.list_3_rec_areas = []
        self.list_3_coord_rec_areas = []
        self.list_3_avg_time_work_rec_areas = []

        # Create work coordinates from work address
        work_address = self.user_vector[2]
        work_coord = call_geocoding_api(work_address)
        print('Work coordinates: ', work_coord)

        # Create time to work feature
        self.df_home_vectors['time_to_work'] = self.df_home_vectors['coordinates'].apply(call_citymapper_api,
                                                                                         work_coord=work_coord,
                                                                                        key_citymapper=SECRET_KEY_CITYMAPPER)
        self.df_home_vectors.dropna(inplace=True)
        print(self.df_home_vectors.head())
        print(self.df_home_vectors.shape[0])

        # Delete unwanted cols
        df_wo_id_coord_area = self.df_home_vectors.copy()
        df_wo_id_coord_area.drop(['id', 'coordinates', 'area'], axis=1, inplace=True)
        print('DF ONLY IMP FEATURES')
        print(df_wo_id_coord_area.head())
        del self.user_vector[2]
        print('USER VECTOR ONLY IMP FEATURES')
        print(self.user_vector)

        # Standardise both user vector and home vectors
        scaler = StandardScaler().fit(df_wo_id_coord_area.values)
        scaled_home_vectors = scaler.transform(df_wo_id_coord_area)
        scaled_user_vector = scaler.transform(np.asarray(self.user_vector).reshape(1, -1))

        # Calculate cosine similarity
        sim_houses_user = cosine_similarity(scaled_home_vectors, scaled_user_vector)

        # Add cosine similarity to homes vector
        self.df_home_vectors['similarity'] = sim_houses_user

        # Group by area and calculate avg of similarity by area
        groups = self.df_home_vectors.groupby('area')

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
            df_area = self.df_home_vectors[self.df_home_vectors['area'] == area]
            avg_time_to_work = df_area['time_to_work'].mean()
            self.list_3_avg_time_work_rec_areas.append(avg_time_to_work)

    def get_rec_areas(self):
        return self.list_3_rec_areas

    def get_rec_areas_coord(self):
        return self.list_3_coord_rec_areas

    def get_rec_areas_time_work(self):
        return self.list_3_avg_time_work_rec_areas


if __name__ == '__main__':
    user_vector = [1, 1000,  'Old St, London', 30]
    recs = RecSys(user_vector).get_rec_areas()
