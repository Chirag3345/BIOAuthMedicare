import random

import config
from server import register as s_reg
from user import (
    register as u_reg,
    login,
    logout,
    update_password,
    update_biometric)


def register_servers(n):
    for i in range(n):
        s_reg(random.getrandbits(64))
    print(n, " new servers registered.\n")


def exit_application():
    exit(0)


def print_help():
    print('############################# Command Reference ###############################')
    print('#    register         <uid> <password> <path_to_biometric>                    #')
    print('#    login            <uid> <password> <biometric_file> <smartcard_file>      #')
    print('#    logout                                                                   #')
    print('#    update_password  <old_password> <new_password> <smartcard_file>          #')
    print('#    update_biometric  <password> <new_biometric_file> <smartcard_file>        #')
    print('#    help                                                                     #')
    print('#    quit                                                                     #')
    print('###############################################################################')
    print('\n')


def main():
    register_servers(config.NUM_SERVERS)

    cmd = ['']

    command_mapping = {
        'register': u_reg,
        'login': login,
        'logout': logout,
        'update_password': update_password,
        'update_biometric': update_biometric,
        'help': print_help,
        'quit': exit_application
    }
    print_help()
    while True:
        cmd = input('$bioAuth.terminal: ')
        cmd = cmd.split()
        try:
            func = command_mapping[cmd[0]]
            func(*cmd[1:])
        except KeyError:
            print("Invalid choice")
        except IndexError:
            pass
        except TypeError:
            print("Invalid arguments")


if __name__ == "__main__":
    main()
