import csv
import glob
import os
import re

import pandas as pd

from scraper import settings


def get_datasets_path():
    dataset_relative_path = os.path.join(settings.PROJECT_PATH, '../datasets')
    dataset_path = os.path.normpath(dataset_relative_path)
    return dataset_path


def get_datasets_path2():
    dataset_relative_path = os.path.join(settings.PROJECT_PATH, '../datasets2')
    dataset_path = os.path.normpath(dataset_relative_path)
    return dataset_path


def munge_data():
    dp = get_datasets_path()
    dp2 = get_datasets_path2()

    ddo_files = glob.glob(os.path.join(dp, '*_ddo_codes.csv'))

    code_dicts = []
    for f in ddo_files:
        df = pd.read_csv(f, dtype={'DDO Code': str})
        treasury = f.split('/')[-1].split('_')[0]
        code_dicts.append({treasury: list(df['DDO Code'].values)})

    for code_dict in code_dicts:
        for treasury, codes in code_dict.items():
            for code in codes:
                code_file_copies = glob.iglob(
                    os.path.join(dp2, '10*_{}*_{}_*copy.csv'.format(treasury, code))
                )
                for f in code_file_copies:
                    print(f)
                    os.remove(f)

                code_files = glob.glob(os.path.join(dp2, '10*_{}*_{}_*.csv'.format(treasury, code)))
                if len(code_files) == 17:
                    name = code_files[0]
                    name = '_'.join(name.split('/')[-1].split('_')[:-1])
                    code_files = sorted(code_files)
                    dfs = [pd.read_csv(f) for f in code_files]
                    temp_df = pd.concat(dfs)
                    temp_df.to_csv(os.path.join(dp, '{}_20170401-20180831.csv'.format(name)))


def extract_major_head_mapping():
    major_head_file = open(os.path.join(get_datasets_path(), 'LMMHA28022017.csv'))
    csv_reader = csv.reader(major_head_file)
    lines = []
    for line in csv_reader:
        lines.append(line[0].strip())

    new_lines = []
    for line in lines:
        splitted = re.search(r'(\d+)[\.\s]*(.*?)(\d+)', line)
        code, desc, pn = splitted.groups()
        code = code.strip()
        desc = desc.strip()
        new_lines.append([code, desc])

    code_map_file = open(os.path.join(get_datasets_path(), 'major_head_mapping.csv'), 'w')
    code_map_writer = csv.writer(code_map_file)
    for line in new_lines:
        code_map_writer.writerow(line)
    code_map_file.close()
