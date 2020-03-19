import random
import time

import config
import server_session as ss
import util
from msrc import register_server
from util import compute_one_way_hash

servers = util.load(config.SERVER_FILE_PATH)

m8 = 0
rs = 0


def register(sid):
    x1 = register_server(sid)
    servers.append((sid, x1))
    util.store(servers, config.SERVER_FILE_PATH)
    # print(servers)


def login1(tsid, m3, m4, m5, ts1):
    global m8, rs
    key_list = [x1 for (sid1, x1) in servers if sid1 == tsid]
    if len(key_list) == 0:
        return 1, 0, 0, 0, 0

    ss.sid = tsid
    ss.x = key_list[0]

    m6 = compute_one_way_hash(str(ss.sid) + str(ss.x))
    m7 = m3 ^ m6
    m8 = compute_one_way_hash(str(m7) + str(ss.x))
    m9 = m4 ^ m8
    m10 = compute_one_way_hash(str(m8) + str(m9) + str(ts1))

    if m10 != m5:
        ss.reset()
        return 2, 0, 0, 0, 0

    rs = random.getrandbits(64)
    ts2 = time.time()

    m11 = compute_one_way_hash(str(m8) + str(m9)) ^ rs
    ss.sk = compute_one_way_hash(str(m6) + str(m8) + str(m9) + str(rs) + str(ts2))
    m12 = compute_one_way_hash(str(ss.sk) + str(m8) + str(m9) + str(ts2))

    return 0, ss.sid, m11, m12, ts2


def login2(m15, ts3):
    m16 = compute_one_way_hash(str(ss.sk) + str(m8) + str(rs) + str(ts3))
    if m16 != m15:
        ss.reset()
        return 1
    return 0


def logout():
    ss.reset()
