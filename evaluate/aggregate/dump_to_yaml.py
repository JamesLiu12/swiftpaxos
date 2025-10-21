import re
import os
from typing import List, Dict, Any
import yaml
from .log_entry import LogEntry, dump_to_yaml

# Protocol -> Client -> Logs
result: Dict[str, Dict[str, List[LogEntry]]] = {}

def parse_log_to_entry(line: str) -> LogEntry | None:
    parts = line.split(' ')
    if len(parts) != 3:
        return None
    date, t, rtt = parts
    if not (is_date(date) and is_time(t) and is_float(rtt)):
        return None
    return LogEntry(date=date, time=t, rtt=float(rtt))

def traverse_results(result_dir: str):
    if not os.path.isdir(result_dir):
        print(f'result_dir not found or not a directory: {result_dir}')
        return

    for proto_name in os.listdir(result_dir):
        proto_path = os.path.join(result_dir, proto_name)
        if not os.path.isdir(proto_path):
            continue

        result[proto_name] = {}

        for client in os.listdir(proto_path):
            if not client.startswith('client'):
                continue
            file_path = os.path.join(proto_path, client)
            if not os.path.isfile(file_path):
                continue

            entries: List[LogEntry] = []

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                    logs = f.readlines()

            for line in (ln.strip() for ln in logs):
                entry = parse_log_to_entry(line)
                if entry:
                    entries.append(entry)

            result[proto_name][client] = entries

def is_useful(log: str):
    data = log.split(' ')
    return len(data) == 3 and is_date(data[0]) and is_time(data[1]) and is_float(data[2])

def is_date(data: str):
    return bool(re.fullmatch(r'\d{4}/\d{2}/\d{2}', data))

def is_time(data: str):
    return bool(re.fullmatch(r'\d{2}:\d{2}:\d{2}', data))

def is_float(data: str):
    return bool(re.fullmatch(r'(?:\d+\.\d*|\.\d+)', data))

if __name__ == '__main__':
    for i in range(11):
        result = {}
        conflict_rate = i * 10
        nfs_path = '/exports/paxos'
        test_name = f'conflict-{conflict_rate}'
        output_file = f'out/conflict{conflict_rate}.yaml'

        result_dir = os.path.join(nfs_path, test_name)

        traverse_results(result_dir)
        dump_to_yaml(result, output_file)
        print(f'YAML written to: {output_file}')