from evaluate.node import Node
import threading
from typing import List, Dict
from .config_loader import ConfigLoader
import time
import sys

def change_config_node(node: Node, conflict_rate: int, proto: str):
    node.change_config(conflict_rate, proto)

if __name__ == "__main__":
    config_loader = ConfigLoader()

    c = sys.argv[1]
    conflict_rate = int(c)
    proto = sys.argv[2]

    threads: List[threading.Thread] = []
    # Master
    threads.append(threading.Thread(target=change_config_node, args=(config_loader.master, conflict_rate, proto)))
    # Servers
    for server in config_loader.servers:
        threads.append(threading.Thread(target=change_config_node, args=(server, conflict_rate, proto)))
    # Clients
    for client in config_loader.clients:
        threads.append(threading.Thread(target=change_config_node, args=(client, conflict_rate, proto)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()