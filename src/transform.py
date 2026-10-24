
import pandas as pd
import json

def transform(data):
    data = json.loads(data)
    data.keys()
    city_gases = data['result']
    city_gases.keys()
    cities = city_gases['cities']

    cities = pd.DataFrame(cities)
    cities.rename(columns={'name':'city_name','midGrade':'mid_grade'}, inplace=True)
    cities.drop(columns=['lowername'], inplace=True)
    return cities