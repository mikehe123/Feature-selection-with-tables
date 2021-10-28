from sys import platform
from struct import unpack
from hashlib import md5
import pandas as pd
import numpy as np

import data


def UBS(p: float, q: float, T: pd.DataFrame, J: str) -> pd.DataFrame:

    def universal_hash(s: str):
        n = 4 if platform == 'win32' else 8
        return float(unpack('L', md5(s.encode('utf8')).digest()[:n])[0]) / 2**32

    feature = T[J].dropna().astype('str')
    prob = (feature.apply(universal_hash))
    universe_sample = [i for i, pr in enumerate(prob) if pr < p]

    T = T.loc[universe_sample]

    sample = T.sample(frac=q)
    return sample


city_sample = UBS(0.6, 0.4, city, 'CountryCode')
country_sample = UBS(0.5, 0.9, country, 'Code')

sample_join_df = pd.merge(city_sample, country_sample,
                          left_on='CountryCode', right_on='Code')
print(sample_join_df.shape)
