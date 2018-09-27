#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import re
import pandas as pd
import numpy as np
import glob


# In[ ]:


from utils import get_filepath, get_munged_filepath, DISTRICTS, DATASETS_PATH, MUNGED_DATASETS_PATH, MAJOR_HEADS
from scraper.settings import PROJECT_PATH


# In[ ]:


def get_normalized_expenditure_dataframe_for_10(df):
    '''
    given a dataframe, the function does following:
        - remove extra rows showing Total.
        - remove Grand Total row because it has redundant data.
        - fill empty rows with forward fill method.
        - drop duplicate rows.
    '''
    if df.index.dtype != 'int64':
        df = df.reset_index()

    # select the columns which have empty values and forward fill them.
    exclude_cols = ['VoucherBillNO', 'BILLS', 'GROSS', 'AGDED', 'BTDED', 'NETPAYMENT']
    cols = [col for col in df.columns if col not in exclude_cols]
    df[cols] = df[cols].replace(r'^\s+$', np.nan, regex=True)
    df[cols] = df[cols].ffill()

    # remove row with Grand Total as it is redundant.
    df = df[(df[:] != 'Grand Total').all(axis=1)]
    df = df[(df['VoucherBillNO'] != 'Total')]

    numeral_cols = ['BILLS', 'GROSS', 'AGDED', 'BTDED', 'NETPAYMENT']
    for col in numeral_cols:
        df.loc[1, col] = df[df['DM.MAJ.SM.MIN.SMN.BUD.VC.PN.SOE'] == 'Total'][col].sum()
    
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    return df


# In[ ]:


def arrange_expenditure_all_query():
    '''
    the function selects files for query 10th i.e. which shows the detailed data with all the fields present,
    in the datasets dir, normalize the data and creates copy csvs from them.
    '''
    def to_include(filename):
        if re.match('10.*Expend.*\d{8}\.csv$', filename):
            return True

    # list all files in datasets dir
    all_files = os.listdir(DATASETS_PATH)
    to_arrange_with_same_logic = filter(to_include, all_files)
    for filename in to_arrange_with_same_logic:
        filepath = get_filepath(filename)
        df = pd.read_csv(filepath, index_col=0)
        try:
            df = get_normalized_expenditure_dataframe_for_10(df)
        except Exception as e:
            print(filepath)
            raise e

        # save in a file with _copy appended to the original file's name.
        to_file = '{}_copy.csv'.format(filepath.split('.csv')[0])
        df.to_csv(to_file, index=False)


# In[ ]:


def get_normalized_receipt_dataframe(df):
    '''
    given a dataframe, the function does following:
        - remove extra rows showing Total.
        - remove Grand Total row because it has redundant data.
        - fill empty rows with forward fill method.
    '''
    # select the columns which have empty values and forward fill them.
    exclude_cols = ['Tenderer', 'Challan', 'NETRECEIPT']
    cols = [col for col in df.columns if col not in exclude_cols]
    df[cols] = df[cols].replace(r'^\s+$', np.nan, regex=True)
    df[cols] = df[cols].ffill()

    # remove row with Grand Total as it is redundant.
    df = df[(df[:] != 'Grand Total').all(axis=1)]
    df = df[(df[:] != 'Total').all(axis=1)]

    df = df.reset_index(drop=True)

    return df


# In[ ]:


def arrange_receipt_files():
    '''
    the function selects files for query 10th i.e. which shows the detailed data with all the fields present,
    in the datasets dir, normalize the data and creates copy csvs from them.
    '''
    def to_include(filename):
        if re.match('01.*Receipt.*\d{8}\.csv$', filename):
            return True

    # list all files in datasets dir
    all_files = os.listdir(DATASETS_PATH)
    to_arrange_with_same_logic = filter(to_include, all_files)
    for filename in to_arrange_with_same_logic:
        filepath = get_filepath(filename)
        df = pd.read_csv(filepath)
        try:
            df = get_normalized_receipt_dataframe(df)
        except Exception as e:
            print(filepath)
            raise e

        # save in a file with _copy appended to the original file's name.
        to_file = get_munged_filepath(filename)
        df.to_csv(to_file , index=False)


# In[ ]:


def get_normalized_expenditure_dataframe(filename):
    '''
    given a filename, the function does following:
        - add START_DATE and END_DATE columns
        - remove Grand Total row because it has redundant data.
        - fill empty rows with forward fill method.
    '''
    df = pd.read_csv(filename)
    
    # set year column
    df['START_DATE'], df['END_DATE'] = re.findall(r'(\d{8})', filename)

    # reset the index
    df = df.reset_index()
    
    # select the columns which have empty values and forward fill them.
    exclude_cols = ['SOEDESC', 'BILLS', 'GROSS', 'AGDED', 'BTDED', 'NETPAYMENT', 'START_DATE', 'END_DATE']
    cols = [col for col in df.columns if col not in exclude_cols]
    df[cols] = df[cols].replace(r'^\s+$', np.nan, regex=True)
    df[cols] = df[cols].ffill()

    # remove row with Grand Total as it is redundant.
    df = df[(df[:] != 'Grand Total').all(axis=1)]

    return df


# In[ ]:


def arrange_expenditure_data():
    '''
    the function selects files in the datasets dir, normalize the data and creates new csvs
    from them.
    '''
    def to_include(filename):
        if re.match('10.*Expend.*\d{8}\.csv$', filename):
            return True

    # list all files in datasets dir
    all_files = os.listdir(DATASETS_PATH)
    to_arrange_with_same_logic = filter(to_include, all_files)
    for filename in to_arrange_with_same_logic:
        filepath = get_filepath(filename)
        try:
            df = get_normalized_expenditure_dataframe_for_10(filepath)
        except Exception as e:
            print(filepath)
            raise e

        # save in a file with _copy appended to the original file's name.
        to_file = '{}_copy.csv'.format(filepath.split('.csv')[0])
        df.to_csv(to_file, index=False)


# In[ ]:


def concatenate_files(query_str):
    '''
    concatenate the copy files.
    '''
    # get all the files to concatenate
    files_to_concatenate = glob.iglob(os.path.join(MUNGED_DATASETS_PATH, query_str))
    
    if any(files_to_concatenate):
        # prepare dataframes from all files
        dataframes = (pd.read_csv(file, index_col=0) for file in files_to_concatenate)
    
        # concatenate the dataframes
        concatenated_frames = pd.concat(dataframes, ignore_index=True)
    
        # construct the iterator again to get the first file's name
        files_to_concatenate = glob.iglob(os.path.join(MUNGED_DATASETS_PATH, query_str))
        to_file = next(files_to_concatenate)
        to_filepath = get_munged_filepath('{}.csv'.format(re.search('(.*[w|W]ise).*csv', to_file).group(1)))
    
        # save the concatenated dataframes to file
        concatenated_frames.to_csv(to_filepath)


# In[ ]:


def wrangle_data(df, col_to_cast_as_category):
    df = df.drop('Unnamed: 0', axis=1)
    ddo_desc_split = df.DDODESC.str.extract('(?P<DDODESC>.*?)-.*(?:OFFICER?|DTO)(?P<DISTRICT>.*)').fillna('')
    df['DDO'], df['DISTRICT'] = ddo_desc_split.DDODESC.str.strip(), ddo_desc_split.DISTRICT.str.strip()
    df[col_to_cast_as_category] = df[col_to_cast_as_category].astype('category')
    return df


# In[ ]:


def wrangle_data_for_consolidated_query(df, cols_to_cast_as_category):
    df = df.drop('Unnamed: 0', axis=1)
    
    # create new column from existing ones.
    cols_to_create = ['TREASURY', 'DDO', 'DDODESC']
    ddo_desc_split = df.DDODESC.str.extract('(?P<TREASURY>\w+)-(?P<DDO>\d+)-(?P<DDODESC>.*)')
    df[cols_to_create] = ddo_desc_split

    # set district using district code mapping.
    df['DISTRICT'] = ddo_desc_split.TREASURY.str[:3]
    df['DISTRICT'] = df['DISTRICT'].map(DISTRICTS)
    
    # extract date from voucher number.
    df['DATE'] = df['VoucherBillNO'].str.extract('Dt:(?P<DATE>.*?)]').fillna('')
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')

    # split the multi value column to single ones.
    cols_to_create = ['DM', 'MAJ', 'SM', 'MIN', 'SMN', 'BUD', 'VC', 'PN', 'SOE']
    col_split = df['DM.MAJ.SM.MIN.SMN.BUD.VC.PN.SOE'].str.extract('(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\w+)-(\w+)-(\w+)-([\w-]+)').fillna('')
    df[cols_to_create] = col_split
    del df['DM.MAJ.SM.MIN.SMN.BUD.VC.PN.SOE']

    df['MAJ'] = df['MAJ'].map(MAJOR_HEADS)

    # convert columns to category to save memory
    df[cols_to_cast_as_category] = df[cols_to_cast_as_category].astype('category')
    df[cols_to_create] = df[cols_to_create].astype('category')

    # reorder columns
    df = df[['DATE', 'DISTRICT', 'TREASURY', 'DDO', 'DDODESC',
             'DM', 'MAJ', 'SM', 'MIN', 'SMN', 'BUD', 'VC', 'PN', 'SOE',
             'VoucherBillNO', 'BILLS', 'GROSS', 'AGDED', 'BTDED', 'NETPAYMENT']]
    
    df.set_index('DATE', drop=True, inplace=True)
    return df

