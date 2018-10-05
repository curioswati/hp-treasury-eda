# cdl-trial-project
Trial project for CivicDataLab.

## Problem Statement

Collect Himachal Pradesh treasury accounts' expenditure and receipts data and perform exploratory analysis.

## Overview

The analysis reports are inside `reports/` directory.

* [Expenditure](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Summary%20Plots.ipynb) and [Receipts](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Receipt%20Summary.ipynb) summaries give overall patterns for different parameters. There is also a [comparative summary](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Comparative%20Summary%20for%20Expenditure%20and%20Receipts.ipynb) of both receipts and expenditure.

* We have top 10 plots for districts based on [DDOs](https://github.com/curioswati/cdl-trial-project/blob/master/reports/District%20Wise%20top%2010%20DDO%20Receipts.ipynb) for receipts, Major heads for [receipts](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Top%2010%20Major%20Heads%20of%20Receipt%20by%20Districts.ipynb) and for [expenditure](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Top%2010%20Major%20Heads%20of%20Expenses%20by%20Districts.ipynb).

* Then there is a Time Series analysis for [receipts](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Receipt%20Time%20series%20for%20districts%20over%20a%20monthly%20timeline.ipynb) and [expenditure](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Time%20series%20for%20districts%20over%20a%20monthly%20timeline.ipynb) for all the districts.

* We can also use a list of Major Heads to see the receipts and expenses done by different districts as is done here for [receipts](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Receipts%20for%20districts%20-%20Major%20Head%20wise.ipynb) and [expenditure](https://github.com/curioswati/cdl-trial-project/blob/master/reports/Expenditure%20by%20districts%20-%20Major%20Head%20wise.ipynb).

## Organisation of the Repository:

#### scraper

Contains the scraping scripts including the spiders which scrapes the datasets and creates CSVs and utils for extra stuff like cleaning old files to get them into proper format to merge with new files collected with different queries.

#### analysis

Contains the notebook modules which have plotting functions. Also a utils and wrangler module which wrangles the data and provides utilities for plots.

#### reports

Contains the analysis reports.

#### datasets

Contains the raw datasets that were scraped.

#### munged_datasets

Contains the munged datasets.

## Status

Expenditure and Receipt analysis is done for FY 2017-18 and a half FY 2018-2019.
