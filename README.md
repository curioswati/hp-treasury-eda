# cdl-trial-project
Trial project for CivicDataLab.

## Problem Statement

Collect Himachal Pradesh treasury accounts' expenditure and receipts data and perform exploratory analysis.

## Overview

You can get the overview of the task by looking at the notebooks in the `reports/` directory.

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

Only part of the task has been completed in which the analysis could be performed on the expenditure datasets from the different DDOs for FY 2017-18.
