import os
from fnmatch import fnmatch
import zipfile
import pandas as pd
from io import BytesIO


def find_all_zips(root, pattern):
    zips = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch(name, pattern):
                zips.append(os.path.join(path, name))
    return zips


def get_zip_values(zip_file_path):
    out_df = pd.DataFrame(columns=['LOGISTICS_1', 'START_TIME'])
    with zipfile.ZipFile(zip_file_path, 'r') as archive:
        for file in archive.filelist:
            new_df = pd.DataFrame(columns=['LOGISTICS_1', 'START_TIME'])
            df = pd.read_csv(BytesIO(archive.read(file)),
                             encoding='utf-8',
                             sep='\t')
            new_df['LOGISTICS_1'] = df['Column2'][df['Column1'] ==
                                                  'LOGISTICS_1'].values
            new_df['START_TIME'] = df['Column2'][df['Column1'] ==
                                                 'START_TIME'].iat[0]
        out_df = out_df.append(new_df, ignore_index=True)
        return out_df


def get_all_values_from_zips(root, pattern):
    zips = find_all_zips(root, pattern)
    df = get_zip_values(zips[0])
    for zip_file in zips[1:]:
        df = df.append(get_zip_values(zip_file), ignore_index=True)
    return df


if __name__ == "__main__":
    root = './all_the_zips'
    pattern = "*.zip"
    df = get_all_values_from_zips(root, pattern)
