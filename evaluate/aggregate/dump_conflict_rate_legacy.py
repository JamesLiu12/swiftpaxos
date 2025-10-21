from .log_entry import LogEntry, load_from_yaml
from typing import List, Dict, Optional
from datetime import datetime
import yaml

# Unit: message / sec
def cal_throughput(entries: List[LogEntry]) -> Optional[float]:
    if not entries:
        return None
    
    entries.sort(key=lambda e: (e.date, e.time))
    to_dt = lambda e: datetime.strptime(f"{e.date} {e.time}", "%Y/%m/%d %H:%M:%S")

    first_time = to_dt(entries[0])
    last_time  = to_dt(entries[-1])

    duration = (last_time - first_time).total_seconds() + entries[-1].rtt * 0.001

    if abs(duration) < 1e-6:
        return None
    
    return len(entries) / duration

def cal_speedup_avg(speedups: Dict[str, float]) -> float:
    vals = speedups.values()
    return sum(vals) / len(speedups)

# def cal_speedup_max(speedups: Dict[str, float]) -> float:
#     return max(speedups.values())

# def cal_speedup_min(speedups: Dict[str, float]) -> float:
#     return min(speedups.values())

# conflict_proto_speedup: Dict[int, Dict[str, Dict[str, float]]] = {}
conflict_proto_speedup: Dict[int, Dict[str, float]] = {}

data_files = [f'out/conflict{i * 10}.yaml' for i in range(8, 11)]

conflict = 80

for data_file in data_files:
    data = load_from_yaml(data_file)

    throughputs: Dict[str, Dict[str, float]] = {}

    for proto, clients in data.items():
        throughputs[proto] = {}
        for client, entries in clients.items():
            throughput = cal_throughput(entries)
            if throughput: 
                throughputs[proto][client] = throughput
                print(f'[conflict-{conflict}] [{proto}] [{client}] troughput: {throughputs[proto][client]}')

    conflict_proto_speedup[conflict] = {}

    for proto, clients in throughputs.items():
        # conflict_proto_speedup[conflict][proto] = {}
        client_speedups: Dict[str, float] = {}
        
        for client, throughput in clients.items():
            if client in throughputs['paxos']:
                client_speedups[client] = throughputs[proto][client] / throughputs['paxos'][client]
                print(f'[conflict-{conflict}] [{proto}] [{client}] speedup: {client_speedups[client]}')

        # conflict_proto_speedup[conflict][proto]['avg'] = cal_speedup_avg(client_speedups)
        # conflict_proto_speedup[conflict][proto]['max'] = cal_speedup_max(client_speedups)
        # conflict_proto_speedup[conflict][proto]['min'] = cal_speedup_min(client_speedups)
        conflict_proto_speedup[conflict][proto] = cal_speedup_avg(client_speedups)

    conflict += 10

proto_conflict_speedup: Dict[str, Dict[int, float]] = {}

for conflict, proto_speedup in conflict_proto_speedup.items():
    for proto, speedup in proto_speedup.items():
        proto_conflict_speedup.setdefault(proto, {})[conflict] = speedup

with open('out/proto_conflict_speedup.yaml', 'w', encoding='utf-8') as f:
    yaml.safe_dump(proto_conflict_speedup, f, sort_keys=False)