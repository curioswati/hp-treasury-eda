
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
DATASETS_PATH = os.path.normpath(os.path.join(PROJECT_PATH, '../datasets'))
DISTRICTS = {'BLP': 'BILASPUR', 'CHM': 'CHAMBA', 'HMR': 'HAMIRPUR',
             'KNG': 'KANGRA', 'KNR': 'KINNAUR', 'KLU': 'KULLU',
             'LHL': 'LAHAUL & SPITI', 'MDI': 'MANDI', 'SML': 'SHIMLA',
             'SMR': 'SIRMAUR', 'SOL': 'SOLAN', 'UNA': 'UNA'}


# In[4]:


def get_filepath(filename):
    '''
    given a filename, the function returns it's filepath joining with datasets dir.
    '''
    return os.path.join(DATASETS_PATH, filename)


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

