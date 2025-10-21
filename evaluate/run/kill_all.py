from evaluate.node import Node
import threading
from typing import List, Dict
from .config_loader import ConfigLoader

def run_node(node: Node):
    node.kill()

if __name__ == "__main__":
    config_loader = ConfigLoader()

    threads: List[threading.Thread] = []
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
    for t in threads:
        t.join()