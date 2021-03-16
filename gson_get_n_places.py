__doc__ = """
Write script locates n places by type and keyword around a destination with assigned coordinates and radius.
The result will be written in JSON format with the extension .geojson

Sử dụng Google Map API
https://developers.google.com/places/web-service/

"""

import json
import requests
import time


def nearby_search(location, radius, type, number_of_places, *keywords):
    result = []
    keywords_list = ','.join([keyword for keyword in keywords])

    with open("api_key.txt", "rt") as f:
        key = f.read()

    nearby_search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}&radius={}&type={}&keyword={}&key={}".format(
        location, radius, type, keywords_list, key)
    ses = requests.Session()
    resp = ses.get(nearby_search_url, timeout=10)
    places = json.loads(resp.text)

    while True:
        for place in places["results"]:
            destination = {
                "name": place["name"],
                "address": place["vicinity"],
                "location": (place["geometry"]["location"]["lat"],
                             place["geometry"]["location"]["lng"])
            }
            result.append(destination)
        if "next_page_token" in places:
            token_next_page_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}&radius={}&type={}&keyword={}&key={}&pagetoken={}".format(
                location, radius, type, keywords_list, key, places["next_page_token"])
            # to make sure get full list of places
            time.sleep(2)
            resp = ses.get(token_next_page_url, timeout=10)
            places = json.loads(resp.text)
        else:
            break
    return result[:number_of_places]


def geojsonfile_creating(list_of_places):
    geojson_feature = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                # avoid misplacing lng and lat
                "coordinates": [place['location'][1],
                                place['location'][0]]},
            "properties": {"name": place["name"]},
        } for place in list_of_places]
    geojson_result = {"type": "FeatureCollection",
                      "features": geojson_feature}
    with open("50_beerpubs.geojson", "wt", encoding="utf-8") as f:
        json.dump(geojson_result, f, ensure_ascii=False, indent=4)


def main():
    number_of_places = 50
    # the coordinates are Ben Thanh market
    coordinates = {"lat": "10.772288668455124", "lng": "106.69828912610187"}
    location = ",".join(list(coordinates.values()))
    radius = 2000
    type = "restaurant"
    keywords = ["beer"]
    places_json = nearby_search(
        location, radius, type, number_of_places, *keywords)
    geojsonfile_creating(places_json)


if __name__ == "__main__":
    main()
