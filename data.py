import pandas as pd
from os import path, listdir, getcwd

# DATA_FOLDER = 'World'
# FULL_DATA_FOLDER = path.join(getcwd(), DATA_FOLDER)

# TABLES = [f.split('.')[0]
#           for f in listdir(FULL_DATA_FOLDER) if f.endswith('.csv')]

# for table in TABLES:
#     globals()[table] = pd.read_csv(f'{FULL_DATA_FOLDER}/{table}.csv')

__all__ = []

# print(__all__)


def get_data(fpath):
    DATA_FOLDER = fpath
    FULL_DATA_FOLDER = path.join(getcwd(), DATA_FOLDER)

    TABLES = [f.split('.')[0]
              for f in listdir(FULL_DATA_FOLDER) if f.endswith('.csv')]

    for table in TABLES:
        globals()[table] = pd.read_csv(f'{FULL_DATA_FOLDER}/{table}.csv')
        __all__.append(table)


get_data('World')
get_data('school')
get_data('Women-Basketball-DB')
get_data('Chess')
get_data('Dataset')
print(__all__)
