from typing import List, Dict, Optional
import re
import yaml
import os

num_of_commands = 1000
conflicts = [i * 10 for i in range(0, 11)]

def read_duration(client: str) -> Optional[float]:
    """Parse the Go-style duration that appears after 'Test took' and return seconds."""
    with open(client, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError(f"No non-empty lines found in {client!r}")

    duration_token: Optional[str] = None
    for candidate in reversed(lines):
        if "Test took" in candidate:
            _, after = candidate.split("Test took", 1)
            duration_token = after.strip().split()[0]
            break

    if duration_token is None:
        return None

    pattern = re.compile(r"(\d+(?:\.\d+)?)(h|ms|µs|μs|us|ns|m|s)")
    unit_to_seconds = {
        "h": 3600.0,
        "m": 60.0,
        "s": 1.0,
        "ms": 1e-3,
        "us": 1e-6,
        "µs": 1e-6,
        "μs": 1e-6,
        "ns": 1e-9,
    }

    total_seconds = 0.0
    for value, unit in pattern.findall(duration_token):
        total_seconds += float(value) * unit_to_seconds[unit]

    if total_seconds == 0.0:
        raise ValueError(f"Unable to parse a duration from {duration_token!r}")

    return total_seconds

proto_conflict_speedup: Dict[str, Dict[int, float]] = {}

for conflict in conflicts:
    dir = f'/exports/paxos/conflict-{conflict}'
    
    proto_client_throughput: Dict[str, Dict[str, float]] = {}
    proto_client_speedup: Dict[str, Dict[str, float]] = {}

    protos = os.listdir(dir)

    for proto in protos:
        proto_client_throughput[proto] = {}
        for client in os.listdir(os.path.join(dir, proto)):
            if not client.startswith('client'): continue
            duration = read_duration(os.path.join(dir, proto, client))
            if not duration: continue
            proto_client_throughput[proto][client] = num_of_commands / duration
            print(f'[{conflict}] [{proto}] [{client}] throughput: {proto_client_throughput[proto][client]}')

    for proto in protos:
        proto_client_speedup[proto] = {}
        for client in proto_client_throughput[proto].keys():
            if not client.startswith('client'): continue
            if not client in proto_client_throughput['paxos']: continue
            proto_client_speedup[proto][client] = proto_client_throughput[proto][client] / proto_client_throughput['paxos'][client]
            print(f'[{conflict}] [{proto}] [{client}] speedup: {proto_client_speedup[proto][client]}')

    for proto in protos:
        speedups = proto_client_speedup[proto].values()
        proto_conflict_speedup.setdefault(proto, {})[conflict] = sum(speedups) / len(speedups)

    with open('out/proto_conflict_speedup.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(proto_conflict_speedup, f, sort_keys=False)