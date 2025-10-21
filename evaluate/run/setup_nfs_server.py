from evaluate.node import Master
from .config_loader import ConfigLoader

if __name__ == "__main__":
    config_loader = ConfigLoader()
    master: Master = config_loader.master
    master.set_up_nfs()