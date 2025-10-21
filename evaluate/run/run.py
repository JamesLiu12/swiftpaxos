from evaluate.node import Node
import threading
from typing import List, Dict
from .config_loader import ConfigLoader
import time

def run_node(node: Node):
    node.run()
    print('Node ran')

def init_node(node: Node):
    node.kill()
    node.init_repo()
    node.init_log()

def check_status(node: Node):
    time.sleep(300)
    while True:
        if not node.is_running():
            return
        time.sleep(120)

if __name__ == "__main__":
    config_loader = ConfigLoader()

    threads: List[threading.Thread] = []

    # Master
    threads.append(threading.Thread(target=init_node, args=(config_loader.master,)))
    # Servers
    for server in config_loader.servers:
        threads.append(threading.Thread(target=init_node, args=(server,)))
    # Clients
    for client in config_loader.clients:
        threads.append(threading.Thread(target=init_node, args=(client,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("All initiated")

    threads = []

    # Master
    threads.append(threading.Thread(target=run_node, args=(config_loader.master,)))
    # Servers
    for server in config_loader.servers:
        threads.append(threading.Thread(target=run_node, args=(server,)))
    # Clients
    for client in config_loader.clients:
        threads.append(threading.Thread(target=run_node, args=(client,)))

    for t in threads:
        t.start()
        t.join()
        time.sleep(3)
    # for t in threads:

    print("All started")

    threads = []

    for client in config_loader.clients:
        threads.append(threading.Thread(target=check_status, args=(client,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    nodes = [config_loader.master] + config_loader.servers + config_loader.clients

    print("All finished")

    threads = []

    for client in config_loader.clients:
        threads.append(threading.Thread(target=lambda node: node.kill(), args=(client,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()