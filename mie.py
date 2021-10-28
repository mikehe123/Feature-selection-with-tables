from ntpath import join
from sys import platform
from struct import unpack
from hashlib import md5
import matplotlib.pyplot as plt
import math
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
        return float(unpack('L', md5(s.encode('utf8')).digest()[:n])[0]) / 2**32

    feature = T[J].dropna().astype('str')
    prob = (feature.apply(universal_hash))
    universe_sample = [i for i, pr in enumerate(prob) if pr < p]

    T = T.loc[universe_sample]

    sample = T.sample(frac=q)
    return sample


class MutualInformationEstimation:

    def __init__(self, esr1: float, t1: pd.DataFrame, j1: str, esr2: float,  t2: pd.DataFrame,  j2: str) -> None:
        self.esr1 = esr1
        self.esr2 = esr2
        self.t1 = t1
        self.t2 = t2
        self.j1 = j1
        self.j2 = j2
        self.freq = self.get_freq()
        self.gammas = self.get_gamma_set()
        self.parameters = self.optimal_sampling_parameters()
        self.variance_centralized = self.get_variance_centralized()
        self.variance_primary_foreign = self.get_variance_pf_key()

    def get_freq(self) -> tuple:
        j1_as_dict = dict(self.t1[self.j1].value_counts())

        j2_as_dict = dict(self.t2[self.j2].value_counts())

        return j1_as_dict, j2_as_dict

    def get_join_count(self):
        join_count = pd.merge(
            self.t1, self.t2, left_on=self.j1, right_on=self.j2).shape[0]
        return join_count

    @staticmethod
    def get_sample(p, q, table, attribute):
        sample = UBS(p, q, table, attribute)
        return sample

    def get_join_count_sample(self, s1, s2):
        j1 = self.j1
        j2 = self.j2
        join_count = pd.merge(s1, s2, left_on=j1, right_on=j2).shape[0]

        return join_count

    @staticmethod
    def get_join_count_estimate(p, q1, q2, sam_join_size):
        i_count_estimate = (1/(p*q1*q2))*sam_join_size
        return i_count_estimate

    # def get_join_sample_size(self):
    #     sample1 = data.UBS(0.9, 1, self.t1, self.j1)
    #     sample2 = data.UBS(0.9, 1, self.t2, self.j2)
    #     sample_size = pd.merge(
    #         sample1, sample2, left_on=self.j1, right_on=self.j2)
    #     return sample_size

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

    def optimal_sampling_parameters(self):
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

    def get_variance_centralized(self):
        p = self.parameters[0]
        esr1 = self.esr1
        esr2 = self.esr2

        gammas = self.gammas
        g11 = gammas[0]
        g12 = gammas[1]
        g21 = gammas[2]
        g22 = gammas[3]

        var_j_count = ((1/p)-1)*g22 + ((1/esr2)-(1/p))*g21 + ((1/esr1) - (1/p))*g12 \
            + ((p/(esr1*esr2)) - (1/esr1) - (1/esr2) + (1/p))*g11
        return var_j_count

    def get_variance_pf_key(self):
        A = self.freq[0]
        B = self.freq[1]
        p = self.esr1

        join_size = 0
        for a, va in A.items():
            for b, vb in B.items():
                if a == b:
                    join_size += float(va)*float(vb)

        variance = ((1/p) - 1) * join_size
        return variance

    def get_variance_manual(self, p, q1, q2, sample_size):

        estimate_jcounts = []
        for i in range(1, sample_size, 1):
            s1 = UBS(p, q1, self.t1, self.j1)
            s2 = UBS(p, q2, self.t2, self.j2)
            sample_jcount = self.get_join_count_sample(
                s1, s2)
            estimate_jcounts.append(
                self.get_join_count_estimate(p, q1, q2, sample_jcount))

        ej_avg = sum(estimate_jcounts)/len(estimate_jcounts)

        manual_vairance = sum(
            [(ej - ej_avg)**2 for ej in estimate_jcounts])/(len(estimate_jcounts) - 1)
        return manual_vairance

    def print_all_stats(self):
        print("ers1: ", self.esr1)
        print("p: ", self.parameters[0])
        print("q1: ", self.parameters[1])
        print("esr2: ", self.esr1)
        print("p: ", self.parameters[0])
        print("q2: ", self.parameters[1])
        print("")
        print("Centralized Variance: ", self.variance_centralized)
        print("Primary Foreign Key Join Variance: ",
              self.variance_primary_foreign)


# city_country = JoinSizeEstimation(
#     0.9, city, 'CountryCode', 0.9, country, 'Code')

# print(city_country.print_all_stats())

# s1 = city_country.get_sample(0.9, 1, city_country.t1, city_country.j1)
# s2 = city_country.get_sample(0.9, 1, city_country.t2, city_country.j2)

# sample_join_size = city_country.get_join_count_sample(s1, s2)
# city_country.get_join_count_estimate(0.9, 1.0, 1.0, sample_join_size)
# print(city_country.get_variance_manual(0.9, 1.0, 1, 100))

# print("hello world")
