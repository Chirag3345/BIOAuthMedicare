import hashlib
import pickle

import numpy
import reedsolo
from memory_profiler import profile

rsc = reedsolo.RSCodec(12)


def load(file):
    try:
        fin = open(file, "rb")
        return pickle.load(fin)
    except FileNotFoundError:
        return []


def store(obj, file):
    fout = open(file, "wb")
    pickle.dump(obj, fout)


def encode(k):
    return int(rsc.encode(k).hex(), 16)


# @profile
def decode(kcw):
    try:
        return rsc.decode(kcw.to_bytes(50, 'big')).decode("utf-8").lstrip('\x00')
    except reedsolo.ReedSolomonError:
        return ""
    except OverflowError:
        return ""


# @profile
def compute_one_way_hash(x):
    return int(hashlib.sha256(x.encode('utf-8')).hexdigest(), 16)


def load_biometric(file_name):
    return numpy.loadtxt(file_name)
