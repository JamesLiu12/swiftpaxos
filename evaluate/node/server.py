from .node import Node
import os

class Server(Node):
    def __init__(self, address: str, user: str, identity_file: str, config_path: str, protocol: str, alias: str):
        super().__init__(address, user, identity_file, config_path, protocol)
        self.alias = alias

    def run(self):
        return self.run_cmd_async(f"{os.path.join(Node.working_dir, 'swiftpaxos')}", 
                            "-run server", 
                            f"-config {self.config_path}", 
                            f"-alias {self.alias}",
                            f"-protocol {self.protocol}",
                            f"-log {os.path.join(Node.nfs_client_path, Node.test_name, self.protocol, self.alias)}")
    
    def mount(self, master_address: str):
        self.run_cmds([
            "sudo apt-get update -y",
            "sudo apt-get install -y nfs-common",
            f"sudo umount -f -l {Node.nfs_client_path}",
            f"sudo mkdir -p {Node.nfs_client_path}",
            f"sudo mount {master_address}:{Node.nfs_server_path} {Node.nfs_client_path}"
            ])
        
    def init_log(self):
        log_dir = os.path.join(Node.nfs_client_path, Node.test_name, self.protocol)
        log_file = os.path.join(log_dir, self.alias)
        self.run_cmd(f"rm -rf {log_file}*")
        self.run_cmd(f"mkdir -p {log_dir}")
        self.run_cmd(f"touch {log_file}")