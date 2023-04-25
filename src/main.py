import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

sl_realtime_key = os.getenv('SL_REALTIME_KEY')
sl_linedata_key = os.getenv('SL_LINEDATA_KEY')


def get_stops():
    api_url = f'https://api.sl.se/api2/LineData.json?key={sl_linedata_key}&model=site'

    response = requests.get(api_url)
    data = response.json()

    stops = []
    for site in data['ResponseData']['Result']:
        stops.append({"name": site['SiteName'], "site_id": site['SiteId']})

    return stops


if __name__ == '__main__':
    stops = get_stops()

    # line14 = []

    # # load ../lines/14.json
    # with open('lines_raw/14.json') as f:
    #     line = json.load(f)
    #     for stop in line["travels"][0]["legs"][0]["intermediateStops"]:
    #         line14.append(stop["name"].lower())

    # # get stopIDs for line 14

    # seen = set()
    # stop_14 = []

    # for stop in line14:
    #     for s in stops:
    #         if  "stadion" in s["name"].lower().strip():
    #             print(s["name"])

    #         if stop.lower() == s["name"].lower() and s["name"] not in seen:
    #             stop_14.append(s)
    #             seen.add(s["name"])



    stop_14 = []
    with open('lines/14.json') as f:
        line = json.load(f)
        for stop in line:
            stop_14.append(stop)

    northbound = set()
    southbound = set()

    closest_stop = {}

    # get realtime data for line 14
    for stop in stop_14:
        api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={sl_realtime_key}&siteid={stop["site_id"]}&timewindow=10'
        response = requests.get(api_url)
        data = response.json()

        for metro in data["ResponseData"]["Metros"]:

            if metro["LineNumber"] != "14":
                continue

            north = True

            if metro["JourneyDirection"] == 1:
                northbound.add(metro["JourneyNumber"])
            else:
                southbound.add(metro["JourneyNumber"])
                north = False

            if metro["DisplayTime"] == "Nu":
                time = 0
            elif ":" in metro["DisplayTime"]:
                continue
            else:
                time = int(metro["DisplayTime"].split(" ")[0])

            if metro["JourneyNumber"] not in closest_stop:
                closest_stop[metro["JourneyNumber"]] = {
                    "time": time, "northbound": north, "stop": stop}
            else:
                if closest_stop[metro["JourneyNumber"]]["time"] > time:
                    closest_stop[metro["JourneyNumber"]] = {
                        "time": time, "northbound": north, "stop": stop}

    # print(json.dumps(closest_stop, indent=4))

    print("\n\n↑↓")
    # print northbound
    for stop in stop_14:
        north = 0
        south = 0
        for journey in closest_stop:
            if closest_stop[journey]["stop"] == stop and closest_stop[journey]["northbound"] == True:
                north = journey
            elif closest_stop[journey]["stop"] == stop and closest_stop[journey]["northbound"] == False:
                south = journey

        if south != 0:
            print(closest_stop[south]["time"], end="")
        else:
            print(" ", end="")


        if north != 0:
            print(closest_stop[north]["time"], end="")
        else: 
            print(" ", end="")

        print(f' {stop["name"]}')