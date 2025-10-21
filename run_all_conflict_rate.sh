#!/bin/bash

tests=(0 1 2 3 4 5 6 7 8 9 10)
for c in "${tests[@]}"; do
    conflict=$((c * 10))
    python3 -m evaluate.run.change_conflict "$conflict"
    python3 -m evaluate.run.change_proto "paxos"
    python3 -m evaluate.run.change_all "$conflict" "paxos"
    python3 -m evaluate.run.run
    python3 -m evaluate.run.kill_all

done
