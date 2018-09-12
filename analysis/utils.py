
# coding: utf-8

# In[1]:


import os
import sys
module_paths = [os.path.abspath(os.path.join(path)) for path in ['.', '..']]
for module_path in module_paths:
    if module_path not in sys.path:
        sys.path.append(module_path)


# In[2]:


from scraper.settings import PROJECT_PATH


# In[3]:


# global vars
datasets_path = os.path.normpath(os.path.join(PROJECT_PATH, '../datasets'))
districts = {'BLP': 'BILASPUR', 'CHM': 'CHAMBA', 'HMR': 'HAMIRPUR',
             'KNG': 'KANGRA', 'KNR': 'KINNAUR', 'KLU': 'KULLU',
             'LHL': 'LAHAUL & SPITI', 'MDI': 'MANDI', 'SML': 'SHIMLA',
             'SMR': 'SIRMAUR', 'SOL': 'SOLAN', 'UNA': 'UNA'}


# In[4]:


def get_filepath(filename):
    '''
    given a filename, the function returns it's filepath joining with datasets dir.
    '''
    return os.path.join(datasets_path, filename)


# In[5]:


def make_readable_amount(tick_val):
    if tick_val < 1000:
        return tick_val
    elif tick_val < 10**6:
        return '{}k'.format(int(float(tick_val)/1000))
    elif tick_val < 10**9:
        return '{}M'.format(int(float(tick_val)/10**6))
    else:
        return '{}B'.format(int(float(tick_val)/10**9))


# In[6]:


def wrangle_data(df, col_to_cast_as_category):
    df = df.drop('Unnamed: 0', axis=1)
    ddo_desc_split = df.DDODESC.str.extract('(?P<DDODESC>.*?)-.*(?:OFFICER?|DTO)(?P<DISTRICT>.*)').fillna('')
    df['DDO'], df['DISTRICT'] = ddo_desc_split.DDODESC.str.strip(), ddo_desc_split.DISTRICT.str.strip()
    df[col_to_cast_as_category] = df[col_to_cast_as_category].astype('category')
    return df


# In[7]:


def wrangle_data_for_consolidated_query(df, cols_to_cast_as_category):
    df = df.drop('Unnamed: 0', axis=1)
    ddo_desc_split = df.DDODESC.str.extract('(?P<TREASURY>\w+?)-(?P<DDO>\d+)')
    df['DISTRICT'] = ddo_desc_split.TREASURY.str[:3]
    df['TREASURY'] = ddo_desc_split.TREASURY.str.strip()
    df['DDO'] = ddo_desc_split.DDO.str.strip()
    df['DISTRICT'] = df['DISTRICT'].map(districts)
    df[cols_to_cast_as_category] = df[cols_to_cast_as_category].astype('category')
    return df

