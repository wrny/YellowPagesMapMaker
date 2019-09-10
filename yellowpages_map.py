import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import folium
import os
import argparse
import sys

# Arg Parsing
description = """Enter in the search term, location and number of pages of
that you want to scrape."""

parser = argparse.ArgumentParser(description=description)

parser.add_argument('-s', '--search_terms', type=str, metavar='', required=True, 
                    help="Enter the search term you want a map for.")

parser.add_argument('-l', '--location', type=str, metavar='', required=True, 
                    help="Enter the location you want a map for.")

parser.add_argument('-p', '--pages', type=int, metavar='', required=True, 
                    help="Enter the number of pages of addresses you want"+ \
                    "to scrape.")

args = parser.parse_args()


def get_geocode(street='1 E 161 St',city='Bronx', state='NY', zip_code="10451"):
    """
    Fetches lat / long coordinates from the US Census Bureau API. All repsonses
    are returned in the form of a dictionary, with "success" / "fail" and if
    successful, the lat / long coordinates in a tuple.
        
    success example: {'success': (40.619125, -73.93426)}
    
    Failure will return a similar dictionary with "fail" as the key, and the 
    value being a string reading: "not able to parse address."
        
    fail example: {"fail":"not able to parse address"}
    """
    street = street.replace(" ", "+")
    street = street.replace(",", "%2C")
    street = street.replace("#", "%23")
        
    city = city.replace(" ", "+")
    city = city.replace(",", "%2C")
    
    search_term = "https://geocoding.geo.census.gov/geocoder/locations/" + \
                  f"address?street={street}&city={city}&state={state}&" + \
                  f"zip={zip_code}&benchmark=Public_AR_Census2010&format=json"
    
    r = requests.get(search_term)
    
    j = json.loads(r.text)
    
    if len(j['result']['addressMatches']) != 0:
        coordinate_dict = j['result']['addressMatches'][0]['coordinates']
        lat, long = coordinate_dict['y'], coordinate_dict['x']
        return {"success": (lat, long)}
    
    else:
        search_term = "https://geocoding.geo.census.gov/geocoder/locations/"+ \
                      f"address?street={street}&city={city}&state={state}"+ \
                      f"&zip={zip_code}&benchmark=4&format=json"
                     
        r = requests.get(search_term)
    
        j = json.loads(r.text)

        if len(j['result']['addressMatches']) != 0:
            coordinate_dict = j['result']['addressMatches'][0]['coordinates']
            lat, long = coordinate_dict['y'], coordinate_dict['x']
            return {"success": (lat, long)}
        
        else:
            return {"fail":"not able to parse address"}

def scrape_yellow_page_addresses(search_terms, location, pages):
    filename = f"{search_terms}_{location}_addresses.txt"
    
    search_terms = search_terms.replace(" ", "+")
    search_terms = search_terms.replace(",", "%2C")
    search_terms = search_terms.replace("#", "%23")
        
    location = location.replace(" ", "+")
    location = location.replace(",", "%2C")
    location = location.replace("#", "%23")
                                    
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write("")
    
    print("Beginning scraping process...")
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"+ \
                        "AppleWebKit/537.36 (KHTML, like Gecko)"+ \
                        "Chrome/76.0.3809.132 Safari/537.36"
                        
    headers = {"User-Agent": user_agent}
    
    for num in range(1, pages+1):
        print(f"Fetching page {num}...")
        url = "https://www.yellowpages.com/search?" + \
              f"search_terms={search_terms}" + \
              f"&geo_location_terms={location}&page={num}"
              
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.find_all("div", {"class":"result"})
    
        for card in cards:
            # print(card)
            soup2 = BeautifulSoup(str(card), 'lxml')
            street = soup2.find('div', {"class":"street-address"})
            locality = soup2.find('div', {"class":"locality"})
            if type(street) is not type(None):
                street = street.text.strip()
                # print(street)
    
            if type(locality) is not type(None):
                locality = locality.text.strip()
                
                try:
                    entry = street+"\t"+locality
                    
                    with open(filename, 'a') as file:
                        file.write(entry+"\n")
                        
                except:
                    continue
                
def prepare_dataframe(search_terms, location):
    """
    This script takes the data scraped and written in text file and prepares a
    Pandas DataFrame. First it separates the street, city, state and zipcode 
    into their own columns, then using the get_geocode() function, writes the 
    'lat' and 'long' columns to the DataFrame, and finally dropping the 
    addresses that aren't real / properly formatted.
    """
    filename = f"{search_terms}_{location}_addresses.txt"
                                
    # Getting all lines from the text document, putting it into the list
    with open(filename) as file:
        address_list = [line.strip() for line in file.readlines()]
        
    # Formats the file / seperates street, city, state, zip_code
    df_container = []
    
    for address in address_list:
        address_split = address.split("\t")
        street = address_split[0]
        city_state_zip = address_split[-1]
        city = city_state_zip.split(",")[0]
        state_zip = city_state_zip.split(",")[-1]
        state = state_zip.split(" ")[1].strip()
        zip_code = state_zip.split(" ")[-1].strip()
        df = pd.DataFrame([(street, city, state, zip_code)])
        df_container.append(df)
    
    try:
        # concatenate all lines
        df_concat = pd.concat(df_container, axis=0)
        
        # add columns
        df_concat.columns = ['street', 'city', 'state', 'zip_code']
        
        # sort by address
        df_concat = df_concat.sort_values("street")
        
        # drop duplicates        
        df_concat = df_concat.drop_duplicates(subset="street", keep=False)
                
        # add index
        df_concat.index = range(len(df_concat))
        
        # add entries to lists
        street_list = df_concat["street"].tolist()
        city_list = df_concat["city"].tolist()
        state_list = df_concat["state"].tolist()
        zip_list = df_concat["zip_code"].tolist()
        
        # create columns for latitude / longitude / enter in blank entries
        df_concat['lat'] = ""
        df_concat['long'] = ""
        
        # iterates through each row of the dataframe to get geocodes
        df_row_count = 0
        
        for street, city, state, zip_code in zip(street_list, city_list, 
                                                 state_list, zip_list):
            print(f"{street} {city} {state} {zip_code}")
            geocode = get_geocode(street, city, state, zip_code)
            if list(geocode.keys())[0] == 'success':
                print(geocode)
                lat, long = list(geocode.values())[0]
                df_concat.loc[df_row_count, 'lat'] = lat
                df_concat.loc[df_row_count, 'long'] = long
                df_row_count += 1
                
            else:
                print(geocode)
                df_row_count += 1
                
        # drop everything without a latitude / where geocoding failed.
        for idx in list(df_concat[df_concat['lat'] == ''].index):
            df_concat = df_concat.drop(idx)
                
        # delete text doc and save csv file.
        os.remove(filename)
        csv_name = f"{search_terms}_{location}_addresses.csv"        
        df_concat.to_csv(csv_name, index=False)
        
        return df_concat
    
    except ValueError:
        print("There were no results from your search. Ending program...")
        sys.exit()

def make_map(DataFrame):
    df_concat = DataFrame
    
    
    lat_list = df_concat['lat'].tolist()
    long_list = df_concat['long'].tolist()
    street_list = df_concat["street"].tolist()
    city_list = df_concat["city"].tolist()
    state_list = df_concat["state"].tolist()
    zip_list = df_concat["zip_code"].tolist()
    
    first_entry = [lat_list[0], long_list[0]]
    
    webmap = folium.Map(location=first_entry, zoom_start=12, 
                        tiles = "Stamen Terrain")
    
    fg = folium.FeatureGroup(name='mymap')
    
    html = """
            Street: {}<br>
            City: {}<br>
            Zip: {}<br>
           """
    
    for street, city, state, zip_code, lat, long in zip(street_list, city_list, 
                                                        state_list, zip_list, 
                                                        lat_list, long_list):
        iframe = folium.IFrame(html=html.format(street, city, zip_code), width=200, 
                           height=100)
        
        fg.add_child(folium.CircleMarker(location=[lat, long], radius=9, 
                                         fill_color='blue', color='grey', 
                                         fill_opacity=0.7, fill=True,
                                         popup=folium.Popup(iframe)))
    
    webmap.add_child(fg)
    webmap.save('map.html')
    
if __name__ == '__main__':
    scrape_yellow_page_addresses(args.search_terms, args.location, args.pages)
    df = prepare_dataframe(args.search_terms, args.location)
    make_map(df)