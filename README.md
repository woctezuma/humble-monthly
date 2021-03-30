# Humble Monthly Bundles  [![Build status][Build image]][Build] [![Updates][Dependency image]][PyUp] [![Python 3][Python3 image]][PyUp] [![Code coverage][Codecov image]][Codecov]

  [Build]: <https://github.com/woctezuma/humble-monthly/actions>
  [Build image]: <https://github.com/woctezuma/humble-monthly/workflows/Python application/badge.svg?branch=master>

  [PyUp]: https://pyup.io/repos/github/woctezuma/humble-monthly/
  [Dependency image]: https://pyup.io/repos/github/woctezuma/humble-monthly/shield.svg
  [Python3 image]: https://pyup.io/repos/github/woctezuma/humble-monthly/python-3-shield.svg

  [Codecov]: https://codecov.io/gh/woctezuma/humble-monthly
  [Codecov image]: https://codecov.io/gh/woctezuma/humble-monthly/branch/master/graph/badge.svg

This repository contains code to analyze the content of past Humble Monthly Bundles.

## Data ##

Data is included in the [`data/`](data/) folder, as downloaded on April 6, 2018.

## Requirements ##

- Install the latest version of [Python 3.X](https://www.python.org/downloads/).

- Install the required packages:

```
pip install -r requirements.txt
```

## Usage ##

- Call the Python script:

```
python plot_time_series.py
```

## Plots ##

Plots can be found in the following folders:
 * [`plots/`](https://github.com/woctezuma/humble-monthly/wiki/Partially-Revealed) with every Humble Monthly Bundle, including the last one which is only partially revealed (Early Unlocks),
 * [`plots_fully_revealed_bundles/`](https://github.com/woctezuma/humble-monthly/wiki/Completely-Revealed) with a constraint to fully-revealed Humble Monthly Bundles.  

An example is shown below, with the time to bundle, i.e. the time between a game release and its appearance in a Humble Monthly bundle. This time can be negative for a game which is released on Steam after it appeared in a Humble Monthly bundle. Please note that only games for which Steam keys are provided for no additional cost to Humble Monthly subscribers are taken into account. 

![Time to bundle](https://github.com/woctezuma/humble-monthly/wiki/plots/time_to_bundle__in_years_.png)

## Addendum

If you like these stats, [check out my other repository](https://github.com/woctezuma/steam-api) with a focus on the Steam store.
