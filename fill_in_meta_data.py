import datetime

from download_json import getTodaysSteamSpyData
from parse_wiki import build_dictionary
from steamspy_utils import compute_all_name_distances, get_release_date_as_datetime, get_release_date_as_str


def list_all_games(bundles):
    game_names = set()
    for bundle_content in bundles.values():
        for game_name in bundle_content:
            game_names.add(game_name)

    return game_names


def match_game_name_with_appID(game_name_input, steamspy_database, num_closest_neighbors=1):
    # Code simplified from find_closest_appID() in schulze_goty.py module in Steam-Era-Goty repository
    (dist, sorted_appIDS) = compute_all_name_distances(game_name_input, steamspy_database)

    closest_appID = sorted_appIDS[0:num_closest_neighbors]

    closest_distance = [dist[appID] for appID in closest_appID]

    closest_name = [steamspy_database[appID]['name'] for appID in closest_appID]

    return (closest_appID, closest_distance, closest_name)


def match_all_game_names_with_appID(game_names, num_closest_neighbors=1):
    steamspy_database = getTodaysSteamSpyData()

    matched_meta_data_dict = dict()

    for game_name in game_names:
        (closest_appID, closest_distance, closest_name) = match_game_name_with_appID(game_name, steamspy_database,
                                                                                     num_closest_neighbors)

        matched_meta_data_dict[game_name] = dict()
        matched_meta_data_dict[game_name]['original-name'] = game_name
        matched_meta_data_dict[game_name]['matched-name'] = closest_name
        matched_meta_data_dict[game_name]['appID'] = closest_appID
        matched_meta_data_dict[game_name]['Levenshtein-distance'] = closest_distance

    return matched_meta_data_dict


def adjust_date_to_first_friday_of_the_month(release_date_as_datetime):
    # Reference: https://stackoverflow.com/a/9847269
    weekday_int = release_date_as_datetime.isoweekday()

    # With ISO, Monday is 1, Tuesday is 2, ..., Sunday is 7.
    friday_int = 5

    if weekday_int <= friday_int:
        # The first Friday of the month happens during the same week as the first day of the month.
        delta_to_next_friday = friday_int - weekday_int
    else:
        # The first Friday of the month happens during the week after the week of the first day of the month.
        num_days_in_a_week = 7
        delta_to_next_friday = num_days_in_a_week + friday_int - weekday_int

    release_date_as_datetime = release_date_as_datetime + datetime.timedelta(days=delta_to_next_friday)

    return release_date_as_datetime


def get_bundle_release_date(bundle_name):
    release_date_str = bundle_name.rsplit('Humble Monthly Bundle')[0].strip()

    # Reference: https://stackoverflow.com/a/6557568/
    release_date_as_datetime = datetime.datetime.strptime(release_date_str, '%B %Y')

    # Find the first Friday of the month
    release_date_as_datetime = adjust_date_to_first_friday_of_the_month(release_date_as_datetime)

    return release_date_as_datetime


def get_game_release_date_with_appID(appID, verbose=False):
    try:
        release_date_as_datetime = get_release_date_as_datetime(appID)
    except ValueError:
        release_date_as_datetime = None

        if verbose:
            release_date = get_release_date_as_str(appID)
            print('[Warning] No release date (' + release_date + ') could be found for appID=' + appID)

    return release_date_as_datetime


def get_game_release_date(game_name, verbose=False):
    meta_data = matched_meta_data_dict[game_name]['appID']

    release_date = None
    appID_try_count = 0

    while (release_date is None) and (appID_try_count < len(meta_data)):
        appID = meta_data[appID_try_count]

        release_date = get_game_release_date_with_appID(appID, verbose)
        appID_try_count += 1

    if (appID_try_count > 1) and verbose:
        print('\nA release date could be found with match#=' + str(appID_try_count))
        print(matched_meta_data_dict[game_name])

    if (release_date is None) and verbose:
        print('No release date could be found for ' + game_name)

    return (release_date, appID_try_count)


if __name__ == '__main__':
    filename = 'data/wiki_humble_monthly.txt'
    bundles = build_dictionary(filename)

    game_names = list_all_games(bundles)

    num_closest_neighbors = 2
    matched_meta_data_dict = match_all_game_names_with_appID(game_names, num_closest_neighbors)

    for bundle_name in bundles.keys():
        release_date = get_bundle_release_date(bundle_name)

    verbose = True

    for game_name in game_names:
        (release_date, appID_try_count) = get_game_release_date(game_name, verbose)
