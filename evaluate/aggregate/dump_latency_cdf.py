from .log_entry import LogEntry, load_from_yaml
from typing import List, Dict, Tuple
from datetime import datetime
import yaml

proto_latencies: Dict[str, List[float]] = {}

data_files = [f'out/conflict{i * 10}.yaml' for i in range(11)]

conflict = 0

for data_file in data_files:
    data = load_from_yaml(data_file)

    for proto, clients in data.items():
        proto_latencies[proto] = []
        for client, entries in clients.items():
            latencies = [entry.rtt for entry in entries]
            proto_latencies[proto] += latencies

    conflict += 10

proto_latency_cdf: Dict[str, List[Tuple[float, float]]] = {}

for proto, latencies in proto_latencies.items():
    latencies = sorted(latencies)
    proto_latency_cdf[proto] = [(latencies[0], 0)]
    num_chunks = 10
    stride = len(latencies) // num_chunks
    left  = len(latencies) % num_chunks
    index = -1
    while index < len(latencies) - 1:
        index += stride
        if left:
            index += 1
            left -= 1
        proto_latency_cdf[proto].append((latencies[index], (index + 1) / len(latencies)))

with open('out/proto_latency_cdf.yaml', 'w', encoding='utf-8') as f:
    yaml.safe_dump(proto_latency_cdf, f, sort_keys=False)