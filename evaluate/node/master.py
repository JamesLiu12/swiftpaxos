from .node import Node
import os

class Master(Node):
    def __init__(self, address: str, user: str, identity_file: str, config_path: str, protocol: str):
        super().__init__(address, user, identity_file, config_path, protocol)

    def run(self):
        return self.run_cmd_async(f"{os.path.join(Node.working_dir, 'swiftpaxos')}", 
                            "-run master", 
                            f"-config {self.config_path}", 
                            f"-protocol {self.protocol}",
                            f"-log {os.path.join(Node.nfs_server_path, Node.test_name, self.protocol, 'master')}")
    def set_up_nfs(self):
        self.run_cmds([
        "sudo apt-get update -y",
        "sudo apt-get install -y nfs-kernel-server",
        f"sudo mkdir -p {Node.nfs_server_path}",
        f"sudo chmod 777 {Node.nfs_server_path}",
        "sudo rm -f /etc/exports",
        "sudo touch /etc/exports",
        f'sudo bash -c "echo {Node.nfs_server_path} *\(rw,no_subtree_check\) >> /etc/exports"',
        "sudo exportfs -ra",
        "sudo systemctl restart nfs-kernel-server"
        ])

    def init_log(self):
        log_dir = os.path.join(Node.nfs_server_path, Node.test_name, self.protocol)
        log_file = os.path.join(log_dir, 'master')
        self.run_cmd(f"rm -rf {log_file}*")
        self.run_cmd(f"mkdir -p {log_dir}")
        self.run_cmd(f"touch {log_file}")