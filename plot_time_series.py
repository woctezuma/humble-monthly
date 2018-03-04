import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import colorConverter as cc

from download_json import getTodaysSteamSpyData
from fill_in_meta_data import build_dictionary_with_metadata


def build_time_series_of_bundle_release_date(bundles_dict):
    # For each monthly bundle, store the exact release date of the bundle

    time_series_bundle_release_date = []

    months_in_chronological_order = sorted(bundles_dict.keys())

    for month in months_in_chronological_order:
        bundle_release_date = bundles_dict[month]['release-date']
        time_series_bundle_release_date.append(bundle_release_date)

    return time_series_bundle_release_date


def build_time_series_of_bundle_content_release_dates(bundles_dict):
    # For each monthly bundle, store the list of release dates the bundled games

    time_series_bundle_content_release_dates = []

    months_in_chronological_order = sorted(bundles_dict.keys())

    for month in months_in_chronological_order:
        bundle_content = bundles_dict[month]['content'].keys()

        game_release_dates = []
        for appID in bundle_content:
            game_release_date = bundles_dict[month]['content'][appID]['release-date']
            game_release_dates.append(game_release_date)

        time_series_bundle_content_release_dates.append(game_release_dates)

    return time_series_bundle_content_release_dates


def build_time_series_of_bundle_content_appIDs(bundles_dict):
    # For each monthly bundle, store the list of appIDs

    time_series_bundle_content_appIDs = []

    months_in_chronological_order = sorted(bundles_dict.keys())

    for month in months_in_chronological_order:
        bundle_content = bundles_dict[month]['content'].keys()

        appIDs = list(bundle_content)

        time_series_bundle_content_appIDs.append(appIDs)

    return time_series_bundle_content_appIDs


def plot_mean_and_CI(mean, lb, ub, x_tick_as_dates=None, color_mean=None, color_shading=None):
    # Reference: https://studywolf.wordpress.com/2017/11/21/matplotlib-legends-for-mean-and-confidence-interval-plots/

    if x_tick_as_dates is None:
        x_tick_as_dates = range(mean.shape[0])

    # plot the shaded range of the confidence intervals
    plt.fill_between(x_tick_as_dates, ub, lb,
                     color=color_shading, alpha=.5)
    # plot the mean on top
    plt.plot(x_tick_as_dates, mean, color_mean)


def display_demo():
    # Reference: https://studywolf.wordpress.com/2017/11/21/matplotlib-legends-for-mean-and-confidence-interval-plots/

    # generate 3 sets of random means and confidence intervals to plot
    mean0 = np.random.random(50)
    ub0 = mean0 + np.random.random(50) + .5
    lb0 = mean0 - np.random.random(50) - .5

    mean1 = np.random.random(50) + 2
    ub1 = mean1 + np.random.random(50) + .5
    lb1 = mean1 - np.random.random(50) - .5

    mean2 = np.random.random(50) - 1
    ub2 = mean2 + np.random.random(50) + .5
    lb2 = mean2 - np.random.random(50) - .5

    # plot the data
    fig = plt.figure(1, figsize=(7, 2.5))
    plot_mean_and_CI(mean0, ub0, lb0, color_mean='k', color_shading='k')
    plot_mean_and_CI(mean1, ub1, lb1, color_mean='b', color_shading='b')
    plot_mean_and_CI(mean2, ub2, lb2, color_mean='g--', color_shading='g')

    class LegendObject(object):
        def __init__(self, facecolor='red', edgecolor='white', dashed=False):
            self.facecolor = facecolor
            self.edgecolor = edgecolor
            self.dashed = dashed

        def legend_artist(self, legend, orig_handle, fontsize, handlebox):
            x0, y0 = handlebox.xdescent, handlebox.ydescent
            width, height = handlebox.width, handlebox.height
            patch = mpatches.Rectangle(
                # create a rectangle that is filled with color
                [x0, y0], width, height, facecolor=self.facecolor,
                # and whose edges are the faded color
                edgecolor=self.edgecolor, lw=3)
            handlebox.add_artist(patch)

            # if we're creating the legend for a dashed line,
            # manually add the dash in to our rectangle
            if self.dashed:
                patch1 = mpatches.Rectangle(
                    [x0 + 2 * width / 5, y0], width / 5, height, facecolor=self.edgecolor,
                    transform=handlebox.get_transform())
                handlebox.add_artist(patch1)

            return patch

    bg = np.array([1, 1, 1])  # background of the legend is white
    colors = ['black', 'blue', 'green']
    # with alpha = .5, the faded color is the average of the background and color
    colors_faded = [(np.array(cc.to_rgb(color)) + bg) / 2.0 for color in colors]

    plt.legend([0, 1, 2], ['Data 0', 'Data 1', 'Data 2'],
               handler_map={
                   0: LegendObject(colors[0], colors_faded[0]),
                   1: LegendObject(colors[1], colors_faded[1]),
                   2: LegendObject(colors[2], colors_faded[2], dashed=True),
               })

    plt.title('Example mean and confidence interval plot')
    plt.tight_layout()
    plt.grid()
    plt.show()

    return


def plot_time_series(x_list, feature_str, x_tick_as_dates=None, color='b'):
    x_vec = np.array([np.array(xi) for xi in x_list])

    mean = np.array([np.mean(xi) for xi in x_vec])
    try:
        sig = np.array([np.std(xi) / np.sqrt(len(xi)) for xi in x_vec])

        confidence_factor = 1.96
        ub = mean + confidence_factor * sig
        lb = mean - confidence_factor * sig
    except TypeError:
        sig = None
        ub = None
        lb = None

    fig = plt.figure(1, figsize=(7, 2.5))
    dotted_color = color + '--'

    if sig is not None:
        plot_mean_and_CI(mean, ub, lb, x_tick_as_dates, color_mean=dotted_color, color_shading=color)
        plt.title('Mean and confidence interval plot of ' + feature_str.lower())
    else:
        plt.plot(x_tick_as_dates, mean, color)
        plt.title('Plot of ' + feature_str.lower())

    plt.ylabel(feature_str)
    plt.xlabel('Timeline since the first Humble Monthly bundle was released')

    plt.tight_layout()
    plt.grid()
    plt.show()

    return


if __name__ == '__main__':
    filename = 'data/wiki_humble_monthly.txt'
    bundles = build_dictionary_with_metadata(filename)

    # Aggregate data

    time_series_bundle_release_date = build_time_series_of_bundle_release_date(bundles)
    print(time_series_bundle_release_date)

    time_series_bundle_content_release_dates = build_time_series_of_bundle_content_release_dates(bundles)
    print(time_series_bundle_content_release_dates)

    time_series_bundle_content_appIDs = build_time_series_of_bundle_content_appIDs(bundles)
    print(time_series_bundle_content_appIDs)

    # SteamSpy

    steamspy_database = getTodaysSteamSpyData()

    # Display the number of Steam games per monthly bundle

    feature_str = 'Number of Steam games'

    x_list = [len(bundle_content) for bundle_content in time_series_bundle_content_appIDs]

    plot_time_series(x_list, feature_str, time_series_bundle_release_date)

    # Display the number of reviews

    feature_str = 'Number of reviews'

    x_list = [[(steamspy_database[appID]['positive'] + steamspy_database[appID]['negative'])
               for appID in bundle_content] for bundle_content in time_series_bundle_content_appIDs]

    plot_time_series(x_list, feature_str, time_series_bundle_release_date)

    # Display the time between game release dates and bundle release date

    feature_str = 'Time between game and bundle releases (in years)'

    x_list = [[(bundle_date - game_date).days / 365.25
               for game_date in content_dates] for (bundle_date, content_dates) in
              zip(time_series_bundle_release_date, time_series_bundle_content_release_dates)]

    plot_time_series(x_list, feature_str, time_series_bundle_release_date)

    # Additional displays

    feature_list = ['score_rank', 'userscore',
                    'positive', 'negative',
                    'owners', 'players_forever',
                    'average_forever', 'median_forever',
                    'price'
                    ]

    for feature_str in feature_list:
        x_list = [[int(steamspy_database[appID][feature_str])
                   for appID in bundle_content] for bundle_content in time_series_bundle_content_appIDs]

        plot_time_series(x_list, feature_str, time_series_bundle_release_date)
