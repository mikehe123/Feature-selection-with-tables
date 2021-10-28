from sys import platform
from struct import unpack
from hashlib import md5

import pandas as pd
import numpy as np

from data import *


def UBS(p: float, q: float, T: pd.DataFrame, J: str) -> pd.DataFrame:
    """
    [summary]
        Universe-Bernoulli Sampling
        (http://www.vldb.org/pvldb/vol13/p547-huang.pdf section 3.2 def 6)

    [Return]
        pd.DataFrame sampled from the given table

    [Parameters]
        p - (float): 0 < p ≤ 1 universe sampling rate
        q - (float): 0 < q ≤ 1 Bernoulli (uniform) sampling rate
        T - (pd.DataFrame): table
        J - (str): column name
    """
    def universal_hash(s: str):
        n = 4 if platform == 'win32' else 8
        return float(unpack('L', md5(s.encode('utf8')).digest()[:n])[0]) / 2**64

    feature = T[J].dropna().astype('str')
    T = T.loc[(feature.apply(universal_hash) < p).index]
    T.sample(frac=q)
    return T


player_sample = UBS(0.5, 0.5, players, 'bioID')
players_teams_sample = UBS(0.5, 0.5, players_teams, 'playerID')

print(player_sample)
print(players_teams_sample)

joined_df = pd.merge(player_sample, players_teams_sample,
                     left_on='bioID', right_on='playerID')

print(joined_df)
print(joined_df.corr())
joined_df.corr().to_csv('correlation.csv')
