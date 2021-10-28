import pandas as pd
from os import path, listdir, getcwd

DATA_FOLDER = 'World'
FULL_DATA_FOLDER = path.join(getcwd(), DATA_FOLDER)

TABLES = [f.split('.')[0]
          for f in listdir(FULL_DATA_FOLDER) if f.endswith('.csv')]

for table in TABLES:
    globals()[table] = pd.read_csv(f'{FULL_DATA_FOLDER}/{table}.csv')

__all__ = TABLES

print(__all__)

# class Database:
#     def __init__(self, data_foler: str) -> None:
#         self.data_folder
