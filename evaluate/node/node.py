from typing import List
import subprocess
import os
from abc import ABC, abstractmethod

class Node(ABC):
    repo_url = "https://github.com/JamesLiu12/PPaxos"
    repo_path = "~/PPaxos/"
    branch = "main"
    working_dir = os.path.join(repo_path, "swiftpaxos")
    nfs_server_path = "/exports/paxos"
    nfs_client_path = "/mnt/nfs/paxos"
    test_name = "1"
    
    def __init__(self, address: str, user: str, identity_file: str, config_path: str, protocol: str):
        self.address = address
        self.user = user
        self.identity_file = identity_file
        self.config_path = os.path.join(Node.working_dir, config_path)
        self.protocol = protocol

    def ssh_cmd(self, *remote_cmd) -> List[str]:
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-i", self.identity_file,
            f"{self.user}@{self.address}",
            *remote_cmd
        ]
        print(" ".join(cmd))
        return cmd
    
    def run_cmd(self, *remote_cmd):
        return subprocess.run(self.ssh_cmd(*remote_cmd))
    
    def run_cmd_async(self, *remote_cmd) -> subprocess.Popen:
        return subprocess.Popen(
            self.ssh_cmd(*remote_cmd),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
    
    def run_cmds(self, remote_cmds: List):
        return [self.run_cmd(cmd) for cmd in remote_cmds]
    
    def init_repo(self):
        check_cmd = self.ssh_cmd(f"test -d {Node.repo_path}")
        dir_exists = subprocess.run(check_cmd).returncode == 0
        if dir_exists:
            return self.run_cmd(f"cd {Node.repo_path} && git fetch origin && (git switch {Node.branch} || git switch -c {Node.branch} --track origin/{Node.branch}) && git pull --ff-only")
        clone_cmd = self.ssh_cmd(f"git clone {Node.repo_url} {Node.repo_path} && cd {Node.working_dir} && git fetch origin && (git switch {Node.branch} || git switch -c {Node.branch} --track origin/{Node.branch}) && git pull --ff-only")
        return subprocess.run(clone_cmd)
    
    def init_go(self):
        return self.run_cmds([
            "sudo apt-get update -y",
            "sudo apt-get install -y golang-go",
            ])
    
    def is_running(self) -> bool:
        check_cmd = self.ssh_cmd("pgrep swiftpaxos")
        result = subprocess.run(check_cmd, capture_output=True)
        print(f'returncode: {result.returncode}')
        return result.returncode == 0

    def kill(self):
        return self.run_cmd("pkill -f swiftpaxos")
    
    def change_config(self, conflict_value: int, proto: str):
        return self.run_cmds([
            f"cd {Node.repo_path} && git reset",
            f"cd {Node.repo_path} && git restore .",
            f"cd {Node.repo_path} && git fetch origin && (git switch {Node.branch} || git switch -c {Node.branch} --track origin/{Node.branch}) && git pull --ff-only",
            f"cd {Node.repo_path} && git reset",
            f"cd {Node.repo_path} && git restore .",
            f"cd {Node.repo_path} && git pull",
            f"cd {self.working_dir} && python3 -m evaluate.run.change_conflict {conflict_value}",
            f"cd {self.working_dir} && python3 -m evaluate.run.change_proto {proto}",
        ])
    
    @abstractmethod
    def init_log(self):
        pass

    @abstractmethod
    def run():
        pass
