import datetime

# noinspection PyPep8Naming
import Levenshtein as lv

from download_json import get_todays_steam_spy_data
from parse_wiki import build_dictionary
from steamspy_utils import compute_all_name_distances, get_release_date_as_datetime, get_release_date_as_str


def list_all_games(bundles):
    game_names = set()
    for bundle_content in bundles.values():
        for game_name in bundle_content:
            game_names.add(game_name)

    return game_names


def match_game_name_with_app_id(game_name_input, steamspy_database, num_closest_neighbors=1):
    # Code simplified from find_closest_appID() in schulze_goty.py module in Steam-Era-Goty repository
    (dist, sorted_app_ids) = compute_all_name_distances(game_name_input, steamspy_database)

    closest_app_id = sorted_app_ids[0:num_closest_neighbors]

    closest_distance = [dist[appID] for appID in closest_app_id]

    closest_name = [steamspy_database[appID]['name'] for appID in closest_app_id]

    return closest_app_id, closest_distance, closest_name


def match_all_game_names_with_app_id(game_names, num_closest_neighbors=1):
    steamspy_database = get_todays_steam_spy_data()

    matched_meta_data_dict = dict()

    for game_name in game_names:
        # noinspection PyPep8
        (closest_app_id, closest_distance, closest_name) = match_game_name_with_app_id(game_name, steamspy_database,
                                                                                       num_closest_neighbors)

        matched_meta_data_dict[game_name] = dict()
        matched_meta_data_dict[game_name]['original-name'] = game_name
        matched_meta_data_dict[game_name]['matched-name'] = closest_name
        matched_meta_data_dict[game_name]['appID'] = closest_app_id
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


def get_game_release_date_with_app_id(app_id, is_verbose=False):
    try:
        release_date_as_datetime = get_release_date_as_datetime(app_id)
    except ValueError:
        release_date_as_datetime = None

        if is_verbose:
            release_date = get_release_date_as_str(app_id)
            print('[Warning] No release date (' + release_date + ') could be found for app_id=' + app_id)

    return release_date_as_datetime


def get_game_release_date(game_name, matched_meta_data_dict, is_verbose=False):
    try:
        meta_data = matched_meta_data_dict[game_name]['appID']
    except KeyError:
        meta_data = []

    release_date = None
    app_id_try_count = 0

    while (release_date is None) and (app_id_try_count < len(meta_data)):
        app_id = meta_data[app_id_try_count]

        release_date = get_game_release_date_with_app_id(app_id, is_verbose)
        app_id_try_count += 1

    if (app_id_try_count > 1) and is_verbose:
        print('\nA release date could be found with match#=' + str(app_id_try_count))
        print(matched_meta_data_dict[game_name])

    if (release_date is None) and is_verbose:
        print('No release date could be found for ' + game_name)

    return release_date, app_id_try_count


def check_if_incorrect_match(game_name, matched_meta_data_dict):
    # Return a boolean which is False if at least one of the following conditions is satisfied:
    # - the Levenshtein distance for game_name is zero,
    # - game_name is among the correct matches (manually detected) which have a positive Levenshtein distance.

    has_zero_levenshtein_distance = bool(matched_meta_data_dict[game_name]['Levenshtein-distance'][0] == 0)

    hard_coded_matches = {
        # Correct matches
        'ABZÛ': 'ABZU',
        'Ashes of the Singularity:Escalation': 'Ashes of the Singularity: Escalation',
        'Company of Heroes 2 (+2 DLCs)': 'Company of Heroes 2',
        'Cthulhu Realms - Full Version': 'Cthulhu Realms',
        'Event0': 'Event[0]',
        'Fidel - Dungeon Rescue': 'Fidel Dungeon Rescue',
        'Kingdom: New Lands Royal Edition': 'Kingdom: New Lands',
        'Legend of Grimrock II': 'Legend of Grimrock 2',
        'Nongünz': 'Nongnz',
        'One Piece: Pirate Warriors 3': 'One Piece Pirate Warriors 3',
        'Sentinels of the Multiverse The Video Game': 'Sentinels of the Multiverse',
        'Alien Isolation': 'Alien: Isolation',
        'Wasteland 2: Directors Cut': 'Wasteland 2: Director\'s Cut',
        'God Eater 2: Rage Burst': 'GOD EATER 2 Rage Burst',
        'God Eater: Resurrection': 'GOD EATER RESURRECTION',
        'Holy Potatoes! We’re in Space?!': 'Holy Potatoes! Were in Space?!',
    }

    is_manually_detected_correct_match_with_positive_levenshtein_distance = bool(game_name in hard_coded_matches.keys())

    # noinspection PyPep8
    is_correct_match = has_zero_levenshtein_distance or \
                       is_manually_detected_correct_match_with_positive_levenshtein_distance

    is_incorrect_match = not is_correct_match

    return is_incorrect_match


def fix_incorrect_match(game_name):
    # Return the fixed appID if the game name is among the incorrect matches (manually detected)
    # Otherwise, return None.

    hard_coded_matches = {
        # Fixes for mismatches
        'Brigador': '274500',
        'Civilization VI': '289070',
        'GoNNER - Press Jump To Die Edition': '437570',
        'Hiveswap': '623940',
        'Jotun': '323580',
        'Layers Of Fear Masterpiece Edition': '391720',
        'NEON STRUCT: Die Augen der Welt': '310740',
        'Okhlos': '400180',
        'Orwell': '491950',
        'Pillars of Eternity - Hero Edition': '291650',
        'RIVE': '278100',
        'Renowned Explorers': '296970',
        'Shoppe Keep Deluxe Edition': '381120',
        'Stikbold!': '429330',
        'Strafe': '442780',
        'The Elder Scrolls Online': '306130',
        'Uurnog': '678850',
        'Call of Duty: Black Ops III Multiplayer Starter Pack': '311210',
        'Dragon\'s Dogma': '367500',
        'Resident Evil 5 Gold Edition': '21690',
        'Life Is Strange': '319630',
    }

    try:
        fixed_app_id = hard_coded_matches[game_name]
    except KeyError:
        fixed_app_id = None

    return fixed_app_id


def fix_matched_meta_data_dict(matched_meta_data_dict, is_verbose=False):
    # Manually fix mismatches

    steamspy_database = get_todays_steam_spy_data()

    all_game_names = list(matched_meta_data_dict.keys())

    for game_name in all_game_names:
        if check_if_incorrect_match(game_name, matched_meta_data_dict):
            fixed_app_id = fix_incorrect_match(game_name)
            if fixed_app_id is not None:
                # Fix incorrect match
                fixed_matched_name = steamspy_database[fixed_app_id]['name']
                fixed_distance = lv.distance(game_name.lower(), fixed_matched_name.lower())

                matched_meta_data_dict[game_name]['matched-name'] = [fixed_matched_name]
                matched_meta_data_dict[game_name]['appID'] = [fixed_app_id]
                matched_meta_data_dict[game_name]['Levenshtein-distance'] = [fixed_distance]
            else:
                # Delete incorrect match
                if is_verbose:
                    print('\nDeleting entry for ' + game_name)
                    print(matched_meta_data_dict[game_name])

                del matched_meta_data_dict[game_name]

    return matched_meta_data_dict


def display_matches(game_names, matched_meta_data_dict):
    # Display every match (useful to manually check and fix mismatches)

    for game_name in sorted(game_names):
        try:
            distance = matched_meta_data_dict[game_name]['Levenshtein-distance'][0]
            if distance > 0:
                # Possible mismatch. Make sure this is actually a good match despite positive distance. Otherwise fix it
                print('>0\t\'' + game_name + '\'\t:\t\'' + matched_meta_data_dict[game_name]['matched-name'][0] + '\',')
            else:
                # Perfect match.
                print('==\t\'' + game_name + '\'\t:\t\'' + matched_meta_data_dict[game_name]['matched-name'][0] + '\',')
        except KeyError:
            # Unfixable Mismatch. This should be either a game not on Steam,
            # or no Steam key was provided to Humble Monthly subscribers.
            print('!=\t\'' + game_name + '\'\t:\t\'' + '\',')

    return


def filter_dictionary_with_meta_data(bundles_raw_dict, matched_meta_data_dict, is_verbose=False):
    # Filter a dictionary so that only games with a known release date are included

    bundles_with_meta_data_dict = dict()

    for bundle_name in bundles_raw_dict.keys():
        release_date = get_bundle_release_date(bundle_name)

        if release_date is not None:

            # noinspection PyCallByClass,PyTypeChecker
            monthly_bundle_id = datetime.datetime.strftime(release_date, '%Y-%m')

            bundles_with_meta_data_dict[monthly_bundle_id] = dict()
            bundles_with_meta_data_dict[monthly_bundle_id]['bundle-name'] = bundle_name
            bundles_with_meta_data_dict[monthly_bundle_id]['release-date'] = release_date
            bundles_with_meta_data_dict[monthly_bundle_id]['content'] = dict()

            bundle_content = bundles_raw_dict[bundle_name]

            for game_name in bundle_content:
                (release_date, appID_try_count) = get_game_release_date(game_name, matched_meta_data_dict, is_verbose)

                if release_date is not None:
                    matched_name = matched_meta_data_dict[game_name]['matched-name'][0]
                    app_id = matched_meta_data_dict[game_name]['appID'][0]

                    bundles_with_meta_data_dict[monthly_bundle_id]['content'][app_id] = dict()
                    bundles_with_meta_data_dict[monthly_bundle_id]['content'][app_id]['game-name'] = matched_name
                    bundles_with_meta_data_dict[monthly_bundle_id]['content'][app_id]['release-date'] = release_date

    return bundles_with_meta_data_dict


def build_dictionary_with_metadata(fname, is_verbose=False):
    bundles = build_dictionary(fname)

    game_names = list_all_games(bundles)

    num_closest_neighbors = 1
    matched_meta_data_dict = match_all_game_names_with_app_id(game_names, num_closest_neighbors)

    matched_meta_data_dict = fix_matched_meta_data_dict(matched_meta_data_dict, is_verbose)

    if is_verbose:
        display_matches(game_names, matched_meta_data_dict)

    bundles_with_meta_data = filter_dictionary_with_meta_data(bundles, matched_meta_data_dict, is_verbose)

    return bundles_with_meta_data


if __name__ == '__main__':
    filename = 'data/wiki_humble_monthly.txt'
    verbose = True
    humble_bundles = build_dictionary_with_metadata(filename, verbose)
    print(humble_bundles)
