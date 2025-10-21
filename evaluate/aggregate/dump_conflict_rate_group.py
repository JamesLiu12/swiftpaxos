from typing import List, Dict, Optional
import re
import yaml
import os
import datetime

conflicts = [i * 10 for i in range(0, 11)]
groups = [i for i in range(1, 6)]
duration = 120

COMMAND_LINE_PATTERN = re.compile(
    r'^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\s+(?P<value>-?\d+(?:\.\d+)?)(?:\s*)$'
)

def _parse_command_timestamp(line: str) -> Optional[datetime.datetime]:
    """Return the timestamp if the line represents a command entry, otherwise None."""
    line = line.strip()
    if not line:
        return None

    match = COMMAND_LINE_PATTERN.match(line)
    if not match:
        return None

    # Ensure the value parses as a float; fail fast on malformed entries.
    try:
        float(match.group('value'))
    except ValueError:
        return None

    return datetime.datetime.strptime(match.group('timestamp'), '%Y/%m/%d %H:%M:%S')


def find_start_time(log_file: str) -> datetime.datetime:
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            ts = _parse_command_timestamp(line)
            if ts is not None:
                return ts

    raise ValueError(f'Could not locate the first command entry in log file: {log_file}')


def get_throuphput(start_time, log_file: str) -> int:
    if isinstance(start_time, str):
        start_time = datetime.datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
    elif not isinstance(start_time, datetime.datetime):
        raise TypeError('start_time must be a datetime or a string formatted as YYYY/MM/DD HH:MM:SS')

    end_time = start_time + datetime.timedelta(seconds=duration)
    count = 0
    coverage_reached = False
    commands_after_start = False

    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            ts = _parse_command_timestamp(line)
            if ts is None:
                continue

            if ts >= start_time:
                commands_after_start = True

            if start_time <= ts < end_time:
                count += 1

            if ts >= end_time:
                coverage_reached = True

    if not commands_after_start:
        raise ValueError(
            f'No command entries found at or after the provided start time ({start_time}) in {log_file}.'
        )

    if not coverage_reached:
        raise ValueError(
            f'Log {log_file} ended before covering the required duration of {duration} seconds '
            f'starting at {start_time}.'
        )

    return count

proto_conflict_speedup: Dict[str, Dict[int, float]] = {}

for conflict in conflicts:
    dir = f'/exports/paxos/conflict-{conflict}'
    
    proto_client_throughput: Dict[str, Dict[str, int]] = {}
    proto_client_speedup: Dict[str, Dict[str, float]] = {}
    proto_group_throughput: Dict[str, Dict[str, int]] = {}
    proto_group_speedup: Dict[str, Dict[str, float]] = {}

    protos = os.listdir(dir)

    proto_start : Dict[str, datetime.datetime] = {}
    # find the latest start time of each proto
    for proto in protos:
        clients = [client for client in os.listdir(os.path.join(dir, proto)) if client.startswith('client')]
        latest_start_time = datetime.datetime(1000, 1, 1) # seconds
        for client in clients:
            log_file = os.path.join(dir, proto, client)
            start_time = find_start_time(log_file)
            if latest_start_time < start_time:
                latest_start_time = start_time

        proto_start[proto] = latest_start_time
        proto_client_throughput[proto] = {}
        proto_group_throughput[proto] = {}

        for group in groups:
            proto_group_throughput[proto][group] = 0

        for client in clients:
            log_file = os.path.join(dir, proto, client)
            group = int(client[7])
            proto_group_throughput[proto][group] += get_throuphput(proto_start[proto], log_file)

    print(proto_group_throughput)
    for proto in protos:
        proto_group_speedup[proto] = {}
        for group in groups:
            proto_group_speedup[proto][group] = proto_group_throughput[proto][group] / proto_group_throughput['paxos'][group]

    paxos_throughput = sum(proto_group_throughput['paxos'].values())
    for proto in protos:
        # speedups = proto_group_speedup[proto].values()
        # proto_conflict_speedup.setdefault(proto, {})[conflict] = sum(speedups) / len(speedups)
        proto_conflict_speedup.setdefault(proto, {})[conflict] = sum(proto_group_throughput[proto].values()) / paxos_throughput
        

    with open('out/proto_conflict_speedup.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(proto_conflict_speedup, f, sort_keys=False)