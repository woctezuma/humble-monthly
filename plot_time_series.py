import pathlib

import matplotlib
import steamspypi

matplotlib.use('Agg')

# noinspection PyPep8
import matplotlib.patches as mpatches

# noinspection PyPep8
import matplotlib.pyplot as plt

# noinspection PyPep8
import numpy as np

# noinspection PyPep8,PyPep8Naming
from matplotlib.colors import colorConverter as cc

# noinspection PyPep8
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


def build_time_series_of_bundle_content_app_ids(bundles_dict):
    # For each monthly bundle, store the list of appIDs

    time_series_bundle_content_app_ids = []

    months_in_chronological_order = sorted(bundles_dict.keys())

    for month in months_in_chronological_order:
        bundle_content = bundles_dict[month]['content'].keys()

        app_ids = list(bundle_content)

        time_series_bundle_content_app_ids.append(app_ids)

    return time_series_bundle_content_app_ids


def plot_mean_and_ci(
    mean,
    lb,
    ub,
    x_tick_as_dates=None,
    color_mean=None,
    color_shading=None,
):
    # Reference: https://studywolf.wordpress.com/2017/11/21/matplotlib-legends-for-mean-and-confidence-interval-plots/

    if x_tick_as_dates is None:
        x_tick_as_dates = range(mean.shape[0])

    # plot the shaded range of the confidence intervals
    plt.fill_between(x_tick_as_dates, ub, lb, color=color_shading, alpha=0.5)
    # plot the mean on top
    plt.plot(x_tick_as_dates, mean, color_mean)


# noinspection PyTypeChecker
def display_demo():
    # Reference: https://studywolf.wordpress.com/2017/11/21/matplotlib-legends-for-mean-and-confidence-interval-plots/

    # generate 3 sets of random means and confidence intervals to plot
    mean0 = np.random.random(50)
    ub0 = mean0 + np.random.random(50) + 0.5
    lb0 = mean0 - np.random.random(50) - 0.5

    mean1 = np.random.random(50) + 2
    ub1 = mean1 + np.random.random(50) + 0.5
    lb1 = mean1 - np.random.random(50) - 0.5

    mean2 = np.random.random(50) - 1
    ub2 = mean2 + np.random.random(50) + 0.5
    lb2 = mean2 - np.random.random(50) - 0.5

    # plot the data
    plt.figure(1, figsize=(7, 2.5))
    plot_mean_and_ci(mean0, ub0, lb0, color_mean='k', color_shading='k')
    plot_mean_and_ci(mean1, ub1, lb1, color_mean='b', color_shading='b')
    plot_mean_and_ci(mean2, ub2, lb2, color_mean='g--', color_shading='g')

    class LegendObject:
        def __init__(self, facecolor='red', edgecolor='white', dashed=False):
            self.facecolor = facecolor
            self.edgecolor = edgecolor
            self.dashed = dashed

        # noinspection PyUnusedLocal
        def legend_artist(self, legend, orig_handle, fontsize, handlebox):
            x0, y0 = handlebox.xdescent, handlebox.ydescent
            width, height = handlebox.width, handlebox.height
            patch = mpatches.Rectangle(
                # create a rectangle that is filled with color
                [x0, y0],
                width,
                height,
                facecolor=self.facecolor,
                # and whose edges are the faded color
                edgecolor=self.edgecolor,
                lw=3,
            )
            handlebox.add_artist(patch)

            # if we're creating the legend for a dashed line,
            # manually add the dash in to our rectangle
            if self.dashed:
                patch1 = mpatches.Rectangle(
                    [x0 + 2 * width / 5, y0],
                    width / 5,
                    height,
                    facecolor=self.edgecolor,
                    transform=handlebox.get_transform(),
                )
                handlebox.add_artist(patch1)

            return patch

    bg = np.array([1, 1, 1])  # background of the legend is white
    colors = ['black', 'blue', 'green']
    # with alpha = .5, the faded color is the average of the background and color
    colors_faded = [(np.array(cc.to_rgb(color)) + bg) / 2.0 for color in colors]

    plt.legend(
        [0, 1, 2],
        ['Data 0', 'Data 1', 'Data 2'],
        handler_map={
            0: LegendObject(colors[0], colors_faded[0]),
            1: LegendObject(colors[1], colors_faded[1]),
            2: LegendObject(colors[2], colors_faded[2], dashed=True),
        },
    )

    plt.title('Example mean and confidence interval plot')
    plt.tight_layout()
    plt.grid()
    plt.show()

    return


def plot_time_series(
    x_list,
    feature_str,
    x_tick_as_dates=None,
    output_folder=None,
    color='b',
):
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

    fig, ax = plt.subplots(dpi=300)
    dotted_color = color + '--'

    if sig is not None:
        plot_mean_and_ci(
            mean,
            ub,
            lb,
            x_tick_as_dates,
            color_mean=dotted_color,
            color_shading=color,
        )
        plt.title(feature_str + ', with 95% confidence')
    else:
        plt.plot(x_tick_as_dates, mean, color)
        plt.title('Plot of ' + feature_str.lower())

    plt.ylabel(feature_str)
    plt.xlabel('Timeline since the first Humble Monthly bundle was released')

    import matplotlib.dates as mdates

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))

    plt.tight_layout()
    plt.grid()

    if output_folder is not None:
        formatted_filename = (
            feature_str.lower().replace(' ', '_').replace('(', '_').replace(')', '_')
        )
        file_extension = '.png'

        pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
        output_filename = output_folder + formatted_filename + file_extension

        fig.savefig(output_filename, bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()

    return


def display_all_data(
    time_series_bundle_release_date,
    time_series_bundle_content_release_dates,
    time_series_bundle_content_app_ids,
    output_folder=None,
):
    # Objective: display prepared data

    steamspy_database = steamspypi.load()

    # Display options

    x_tick_as_dates = time_series_bundle_release_date

    # Display the number of Steam games per monthly bundle

    feature_str = 'Number of Steam games'

    x_list = [
        len(bundle_content) for bundle_content in time_series_bundle_content_app_ids
    ]

    plot_time_series(x_list, feature_str, x_tick_as_dates, output_folder)

    # Display the number of reviews

    feature_str = 'Number of reviews'

    x_list = [
        [
            (
                steamspy_database[appID]['positive']
                + steamspy_database[appID]['negative']
            )
            for appID in bundle_content
        ]
        for bundle_content in time_series_bundle_content_app_ids
    ]

    plot_time_series(x_list, feature_str, x_tick_as_dates, output_folder)

    # Display the time between game release dates and bundle release date

    feature_str = 'Time to bundle (in years)'

    x_list = [
        [(bundle_date - game_date).days / 365.25 for game_date in content_dates]
        for (bundle_date, content_dates) in zip(
            time_series_bundle_release_date,
            time_series_bundle_content_release_dates,
        )
    ]

    plot_time_series(x_list, feature_str, x_tick_as_dates, output_folder)

    # Additional displays

    feature_list = [
        'score_rank',
        'userscore',
        'positive',
        'negative',
        'owners',
        'players_forever',
        'average_forever',
        'median_forever',
        'price',
    ]

    for feature_str in feature_list:
        try:
            x_list = [
                [
                    int(steamspy_database[appID][feature_str])
                    for appID in bundle_content
                    # Ignore empty features. NB: It only happened once for appID=438790 ('Random Access Murder') for
                    # which SteamSpy shows an empty string as 'score_rank' due to 'userscore' being '0', which is
                    # likely a bug.
                    if steamspy_database[appID][feature_str] != ''
                ]
                for bundle_content in time_series_bundle_content_app_ids
            ]

        except ValueError:
            # Catch problem due to SteamSpy providing a range of owners instead of a point-estimate.
            print('Impossible conversion to int for feature = ' + feature_str)
            continue
        except KeyError:
            print('Impossible to find feature = ' + feature_str)
            continue

        plot_time_series(x_list, feature_str, x_tick_as_dates, output_folder)

    return


def prepare_all_data_for_display(bundles, verbose=False):
    # Objective: prepare data for display

    time_series_bundle_release_date = build_time_series_of_bundle_release_date(bundles)
    if verbose:
        print(time_series_bundle_release_date)

    time_series_bundle_content_release_dates = (
        build_time_series_of_bundle_content_release_dates(bundles)
    )
    if verbose:
        print(time_series_bundle_content_release_dates)

    time_series_bundle_content_app_ids = build_time_series_of_bundle_content_app_ids(
        bundles,
    )
    if verbose:
        print(time_series_bundle_content_app_ids)

    return (
        time_series_bundle_release_date,
        time_series_bundle_content_release_dates,
        time_series_bundle_content_app_ids,
    )


def plot_all_time_series(
    bundles,
    save_to_file=False,
    verbose=False,
    remove_last_bundle_because_only_early_unlocks=False,
):
    # Prepare data

    (
        time_series_bundle_release_date,
        time_series_bundle_content_release_dates,
        time_series_bundle_content_app_ids,
    ) = prepare_all_data_for_display(bundles, verbose)

    # Remove the last bundle if it is not fully known: typically if only the Early Unlocks are known at runtime.

    if remove_last_bundle_because_only_early_unlocks:
        time_series_bundle_release_date = time_series_bundle_release_date[:-1]
        time_series_bundle_content_release_dates = (
            time_series_bundle_content_release_dates[:-1]
        )
        time_series_bundle_content_app_ids = time_series_bundle_content_app_ids[:-1]

    # Display prepared data

    if save_to_file:
        if remove_last_bundle_because_only_early_unlocks:
            output_folder = 'plots_fully_revealed_bundles/'
        else:
            output_folder = 'plots/'
    else:
        output_folder = None

    display_all_data(
        time_series_bundle_release_date,
        time_series_bundle_content_release_dates,
        time_series_bundle_content_app_ids,
        output_folder,
    )

    return


def main():
    filename = 'data/wiki_humble_monthly.txt'
    humble_bundles = build_dictionary_with_metadata(filename)

    save_to_file = True
    is_verbose = True

    # Remove the last bundle if it is not fully known: typically if only the Early Unlocks are known at runtime.
    remove_last_bundle_because_only_early_unlocks = False

    plot_all_time_series(
        humble_bundles,
        save_to_file,
        is_verbose,
        remove_last_bundle_because_only_early_unlocks,
    )

    return True


if __name__ == '__main__':
    main()
