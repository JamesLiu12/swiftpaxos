from typing import Dict
import yaml
import matplotlib.pyplot as plt

with open('out/proto_conflict_speedup.yaml', 'r', encoding='utf-8') as f:
    proto_conflict_speedup: Dict[str, Dict[str | int, float]] = yaml.safe_load(f) or {}

all_conflict_rates = sorted({
    int(cr) for proto_speedup in proto_conflict_speedup.values() for cr in proto_speedup.keys()
})

proto_style = {
    "SwiftPaxos": dict(color="#F39C12", marker="x", linestyle="-", linewidth=2),
    "CURP+":      dict(color="#3B82F6", marker="+", linestyle="-"),
    "EPaxos":     dict(color="#1ABC9C", marker="^", linestyle="-"),
    "FastPaxos":  dict(color="#0EA5E9", marker="o", linestyle="-"),
    "GPaxos":     dict(color="#6366F1", marker="s", linestyle="-"),
    "N2P":        dict(color="#16A34A", marker="v", linestyle="-"),
    "paxos":      dict(color="#000000", marker="o", linestyle="-", linewidth=1.5),
}

fig, ax = plt.subplots(1, 1, figsize=(6.5, 4.0))

for proto, cr_map in proto_conflict_speedup.items():
    ys = []
    for cr in all_conflict_rates:
        val = cr_map.get(cr, cr_map.get(str(cr)))
        ys.append(val if val is not None else None)

    style = proto_style.get(proto, dict(marker="o", linestyle="-"))
    ax.plot(all_conflict_rates, ys, label=proto, **style)

ax.set_xlim(min(all_conflict_rates), max(all_conflict_rates))
ax.set_xlabel("conflict rate (%)")
ax.set_ylabel("speedup")
ax.set_title("Speedup vs Conflict Rate")
ax.grid(True, linestyle=":", alpha=0.4)

if all_conflict_rates and (min(all_conflict_rates) >= 0 and max(all_conflict_rates) <= 100):
    ax.set_xticks(list(range(0, 101, 20)))

# ax.set_ylim(0.9, 2.0)

ax.legend(ncol=3, loc="upper left", fontsize=9, frameon=False)

plt.tight_layout()
plt.savefig("out/speedup_vs_conflict.png", dpi=200, bbox_inches="tight")