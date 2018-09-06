
# coding: utf-8

# In[2]:


import os
import sys
module_paths = [os.path.abspath(os.path.join(path)) for path in ['.', '..']]
for module_path in module_paths:
    if module_path not in sys.path:
        sys.path.append(module_path)


# In[3]:


from scraper.settings import PROJECT_PATH


# In[4]:


# global vars
datasets_path = os.path.normpath(os.path.join(PROJECT_PATH, '../datasets'))


# In[5]:


def get_filepath(filename):
    '''
    given a filename, the function returns it's filepath joining with datasets dir.
    '''
    return os.path.join(datasets_path, filename)


# In[6]:


def make_readable_amount(tick_val):
    if tick_val < 1000:
        return tick_val
    elif tick_val < 10**6:
        return '{}k'.format(int(float(tick_val)/1000))
    elif tick_val < 10**9:
        return '{}M'.format(int(float(tick_val)/10**6))
    else:
        return '{}B'.format(int(float(tick_val)/10**9))


# In[7]:


def wrangle_data(df):
    df = df.drop('Unnamed: 0', axis=1)
    ddo_desc_split = df.DDODESC.str.extract('(?P<DDODESC>.*?)-.*(?:OFFICER?|DTO)(?P<DISTRICT>.*)')
    df['DDO'], df['DISTRICT'] = ddo_desc_split.DDODESC.str.strip(), ddo_desc_split.DISTRICT.str.strip()
    df['SOEDESC'] = df['SOEDESC'].astype('category')
    return df

