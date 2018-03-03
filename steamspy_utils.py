import datetime
import json
import pathlib

import Levenshtein as lv
import requests


def compute_all_name_distances(game_name_input, steamspy_database):
    dist = dict()

    lower_case_input = game_name_input.lower()

    for appID in steamspy_database.keys():
        str = steamspy_database[appID]['name']

        # Compare names in lower cases, to avoid mismatches for Tekken vs. TEKKEN, or Warhammer vs. WARHAMMER
        dist[appID] = lv.distance(lower_case_input, str.lower())

    sorted_appIDS = sorted(dist.keys(), key=lambda x: dist[x])

    return (dist, sorted_appIDS)


def get_appdetails_filename(appID):
    data_path = "data/appdetails/"

    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    output_file = "appID_" + appID + ".json"
    data_filename = data_path + output_file

    return data_filename


def download_appdetails(appID):
    api_url = "http://store.steampowered.com/api/appdetails/"

    defaults = {
        'json': '1',
    }

    req_data = dict(defaults)
    req_data['appids'] = appID

    resp_data = requests.get(api_url, params=req_data)

    result = resp_data.json()

    request_success_flag = result[appID]['success']

    if request_success_flag:
        data_filename = get_appdetails_filename(appID)

        with open(data_filename, "w") as out_file:
            out_file.write(json.dumps(result))

    return result


def get_release_date_as_str(appID):
    try:
        data_filename = get_appdetails_filename(appID)

        with open(data_filename, 'r', encoding="utf8") as in_json_file:
            result = json.load(in_json_file)
    except FileNotFoundError:
        result = download_appdetails(appID)

    try:
        appID_release_date = result[appID]['data']['release_date']['date']
    except KeyError:
        appID_release_date = None

    return appID_release_date


def get_release_date_as_datetime(appID):
    release_date = get_release_date_as_str(appID)

    try:
        # Reference: https://stackoverflow.com/a/6557568/
        appID_release_date_as_datetime = datetime.datetime.strptime(release_date, '%d %b, %Y')
    except TypeError:
        appID_release_date_as_datetime = None

    return appID_release_date_as_datetime


def get_release_year(appID):
    release_date = get_release_date_as_datetime(appID)

    if release_date is not None:
        release_year = release_date.year
    else:
        release_year = -1

    return release_year
