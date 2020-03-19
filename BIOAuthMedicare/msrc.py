import config
import util
from util import compute_one_way_hash

servers = util.load(config.MSRC_SERVER_FILE_PATH)
users = util.load(config.MSRC_USER_FILE_PATH)
krc = config.MSRC_SECRET_KEY


def register_server(sid):
    x = compute_one_way_hash(str(sid) + krc)
    servers.append((sid, x))
    util.store(servers, config.MSRC_SERVER_FILE_PATH)
    return x


def register_user(uid, pwd):
    auth_params = []
    for (sid, x) in servers:
        a = compute_one_way_hash(str(uid) + str(x)) ^ pwd
        p = compute_one_way_hash(str(sid) + str(x)) ^ pwd
        auth_params.append((sid, a, p))
        users.append((uid, compute_one_way_hash(str(pwd) + str(x))))
    util.store(users, config.MSRC_USER_FILE_PATH)
    return auth_params
