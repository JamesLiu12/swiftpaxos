from ..node import *
import threading
from typing import List
from .config_loader import ConfigLoader

def init_master(master: Master):
    master.init_go()
    master.init_repo()
    master.set_up_nfs()

def init_other(server: Server | Client, master_address: str):
    server.init_go()
    server.init_repo()
    server.mount(master_address)

if __name__ == "__main__":
    config_loader = ConfigLoader()

    threads: List[threading.Thread] = []
    # Master
    init_master(config_loader.master)
    # Servers
    for server in config_loader.servers:
        threads.append(threading.Thread(target=init_other, args=(server, config_loader.master.address)))
    # Clients
    for client in config_loader.clients:
        threads.append(threading.Thread(target=init_other, args=(client, config_loader.master.address)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()