from ntpath import join
from sys import platform
from struct import unpack
from hashlib import md5
from typing_extensions import ParamSpecKwargs
import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np

from data import *
import statistics


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
        return float(unpack('L', md5(s.encode('utf8')).digest()[:n])[0]) / 2**32

    feature = T[J].dropna().astype('str')
    prob = (feature.apply(universal_hash))
    universe_sample = [i for i, pr in enumerate(prob) if pr < p]

    T = T.loc[universe_sample]

    sample = T.sample(frac=q)
    return sample


class queryEstimator:

    def __init__(self, esr1: float, t1: pd.DataFrame, j1: str, esr2: float,  t2: pd.DataFrame,  j2: str) -> None:
        self.esr1 = esr1
        self.esr2 = esr2
        self.t1 = t1
        self.t2 = t2
        self.j1 = j1
        self.j2 = j2
        self.freq = self.get_freq()
        self.gammas = self.get_gamma_set()
        self.betas = self.get_beta_set()

        self.jc_parameters = self.join_count_optimal_sampling_parameters()
        self.sum_parameters = self.sum_optimal_sampling_parameters()

    def get_freq(self) -> tuple:
        j1_as_dict = dict(self.t1[self.j1].value_counts())
        j2_as_dict = dict(self.t2[self.j2].value_counts())

        return j1_as_dict, j2_as_dict

    def get_gamma_set(self):
        def get_gamma(A, B, i, j):
            c = 0
            for a, va in A.items():
                for b, vb in B.items():
                    if a == b:
                        c += (float(va)**i) * (float(vb)**j)
            return c

        A = self.freq[0]
        B = self.freq[1]
        g11 = get_gamma(A, B, 1, 1)
        g12 = get_gamma(A, B, 1, 2)
        g21 = get_gamma(A, B, 2, 1)
        g22 = get_gamma(A, B, 2, 2)

        return (g11, g12, g21, g22)

    def join_count_optimal_sampling_parameters(self):
        gammas = self.gammas
        g11 = gammas[0]
        g12 = gammas[1]
        g21 = gammas[2]
        g22 = gammas[3]
        esr1 = self.esr1
        esr2 = self.esr2

        numerator = esr1 * esr2 * (g22 - g12 - g21 + g11)
        fraction = numerator / g11
        sqrt = math.sqrt(fraction)

        p = min(1, max(esr1, esr2, sqrt))
        q1 = self.esr1/p
        q2 = self.esr2/p

        return (p, q1, q2)

    def get_beta_set(self):
        mean = statistics.mean(self.j1)

    def sum_optimal_sampling_parameters(self):
        pass
