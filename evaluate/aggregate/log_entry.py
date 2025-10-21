from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import os
import yaml

@dataclass
class LogEntry:
    date: str
    time: str
    rtt: float

def dump_to_yaml(data: Dict[str, Dict[str, List[LogEntry]]], path: str):
    serializable: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for proto, clients in data.items():
        serializable[proto] = {}
        for client, entries in clients.items():
            serializable[proto][client] = [asdict(e) for e in entries]

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(serializable, f, sort_keys=False)

def load_from_yaml(path: str) -> Dict[str, Dict[str, List[LogEntry]]]:
    with open(path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f) or {}

    result: Dict[str, Dict[str, List[LogEntry]]] = {}
    for proto, clients in raw.items():
        result[proto] = {}
        for client, entries in (clients or {}).items():
            restored: List[LogEntry] = []
            if entries:
                for item in entries:
                    restored.append(
                        LogEntry(
                            date=item.get('date', ''),
                            time=item.get('time', ''),
                            rtt=float(item.get('rtt', '')),
                        )
                    )
            result[proto][client] = restored
    return result