import os
import random
import shutil
import time
import uuid

import numpy
from memory_profiler import profile

import config
import server
import user_session as urs
import util
from msrc import register_user
from util import compute_one_way_hash


def compute_cancellable_template(biom, tp):
    return hash(tuple(biom.dot(tp)))


# @profile
def register(uid, pw, biom_file):
    uid = int(uid)
    biom = util.load_biometric(biom_file)
    tp = numpy.random.rand(4)
    ct = compute_cancellable_template(biom, tp)
    k = str(uuid.uuid1())
    kcw = util.encode(k)
    ltk = kcw ^ ct
    pwd = compute_one_way_hash(str(uid) + k + pw)
    auth_params = register_user(uid, pwd)
    f = compute_one_way_hash(str(uid) + str(pwd) + str(ct))
    smart_card = (auth_params, tp, ltk, compute_one_way_hash(k), f)

    store_user_data(biom_file, smart_card, uid)
    print("Successfully registered user: ", uid)
    return 0


def store_user_data(biom_file, smart_card, uid):
    dir_path = os.path.join(config.USER_DATA_PATH, str(uid) + "_" + str(int(time.time())))
    os.mkdir(dir_path)
    shutil.copy(biom_file, dir_path)
    file_name = str(uuid.uuid1()) + ".smartcard"
    file_path = os.path.join(dir_path, file_name)
    util.store(smart_card, file_path)
    print("Smartcard created: ", file_name)


# @profile
def login(uid, pw, biom_file, smartcard_file):
    biom = util.load_biometric(biom_file)
    (auth_params, tp, ltk, kh, f) = util.load(smartcard_file)
    urs.uid = int(uid)
    urs.ct = compute_cancellable_template(biom, tp)
    urs.k = util.decode(ltk ^ urs.ct)

    if kh != compute_one_way_hash(urs.k):
        print("User authentication failed: Incorrect biometric")
        urs.reset()
        return 1

    pwd = compute_one_way_hash(str(urs.uid) + urs.k + pw)
    fx = compute_one_way_hash(str(urs.uid) + str(pwd) + str(urs.ct))
    if fx != f:
        print("User authentication failed: Incorrect user credentials (username/password)")
        urs.reset()
        return 1

    rc = random.getrandbits(64)
    ts1 = time.time()
    sid, a, p = auth_params[0]
    m1 = a ^ pwd
    m2 = p ^ pwd
    m3 = urs.uid ^ m2
    m4 = m1 ^ rc
    m5 = compute_one_way_hash(str(m1) + str(rc) + str(ts1))

    err, sid, m11, m12, ts2 = server.login1(sid, m3, m4, m5, ts1)

    if err == 1:
        print("Server not found")
        urs.reset()
        return 1
    if err == 2:
        print("Server authentication failed")
        urs.reset()
        return 1

    m13 = m11 ^ compute_one_way_hash(str(m1) + str(rc))
    urs.sk = compute_one_way_hash(str(m2) + str(m1) + str(rc) + str(m13) + str(ts2))
    m14 = compute_one_way_hash(str(urs.sk) + str(m1) + str(rc) + str(ts2))

    if m12 != m14:
        print("Failed to setup session key: Verification failed at user end")
        urs.reset()
        return 1

    ts3 = time.time()
    m15 = compute_one_way_hash(str(urs.sk) + str(m1) + str(m13) + str(ts3))

    if server.login2(m15, ts3) == 1:
        print("Failed to setup session key: Verification failed at server end")
        urs.reset()
        return 1
    print("Login successful!")
    printf("It is successful")
    print("Session key: ", urs.sk)

    return 0


def is_logged_in():
    if urs.sk == 0:
        print("Not logged in")
        return False
    return True


def logout():
    if not is_logged_in():
        return 1

    urs.reset()
    server.logout()
    print("Successfully logged out!")


def update_password(pw_old, pw_new, smartcard_file):
    if not is_logged_in():
        return 1

    (auth_params, tp, ltk, kh, f) = util.load(smartcard_file)

    pwd_old = compute_one_way_hash(str(urs.uid) + urs.k + pw_old)
    fx = compute_one_way_hash(str(urs.uid) + str(pwd_old) + str(urs.ct))
    if fx != f:
        print("Incorrect password")
        urs.reset()
        return 1

    pwd_new = compute_one_way_hash(str(urs.uid) + urs.k + pw_new)

    auth_params_new = []
    for sid, a, p in auth_params:
        a_new = a ^ pwd_old ^ pwd_new
        p_new = p ^ pwd_old ^ pwd_new
        auth_params_new.append((sid, a_new, p_new))

    f_new = compute_one_way_hash(str(urs.uid) + str(pwd_new) + str(urs.ct))
    util.store((auth_params_new, tp, ltk, kh, f_new), smartcard_file)
    print("Password updated successfully")
    return 0


def update_biometric(pw, biom_file, smartcard_file):
    if not is_logged_in():
        return 1

    biom = util.load_biometric(biom_file)
    (auth_params, tp, ltk, kh, f) = util.load(smartcard_file)
    pwd = compute_one_way_hash(str(urs.uid) + urs.k + pw)
    fx = compute_one_way_hash(str(urs.uid) + str(pwd) + str(urs.ct))
    if fx != f:
        print("Incorrect password")
        urs.reset()
        return 1

    tp_new = numpy.random.rand(4)
    ct_new = compute_cancellable_template(biom, tp_new)
    ltk_new = ltk ^ urs.ct ^ ct_new
    f_new = compute_one_way_hash(str(urs.uid) + str(pwd) + str(ct_new))
    util.store((auth_params, tp_new, ltk_new, kh, f_new), smartcard_file)
    print("Fingerprint updated successfully")
    return 0
