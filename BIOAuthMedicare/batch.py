import glob
import random

import config
from server import register as s_reg
from user import register as u_reg, login

PASSWORD_PREFIX = "samplePassword"


def register_servers(n):
    for i in range(n):
        s_reg(random.getrandbits(64))
    print(n, " new servers registered.\n")


def register_all_users():
    for i in range(1, 2001):
        uid = str(i).rjust(4, '0')
        pw = PASSWORD_PREFIX + uid
        path = glob.glob("./Images/" + uid + "/f*.xyt")[0]
        u_reg(uid, pw, path)


def login_all_users():
    for direc in glob.glob("./UserData/*"):
        uid = direc[11:]
        uid = uid.split('_', 1)[0]
        uid = uid.rjust(4, '0')
        pw = PASSWORD_PREFIX + uid
        biom = glob.glob(direc + "/*.xyt")[0]
        sc = glob.glob(direc + "/*.smartcard")[0]
        login(uid, pw, biom, sc)


def main():
    register_servers(config.NUM_SERVERS)
    register_all_users()
    login_all_users()


if __name__ == "__main__":
    main()
