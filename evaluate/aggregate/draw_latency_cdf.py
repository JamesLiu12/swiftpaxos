from typing import Dict, List, Tuple, Optional, Union
import yaml
import matplotlib.pyplot as plt
import numpy as np

ProtoCdf = Dict[str, List[Tuple[float, float]]]

PROTO_STYLE: Dict[str, Dict] = {
    "SwiftPaxos": dict(color="#F39C12", marker="x", linestyle="-", linewidth=2, markersize=5),
    "CURP+":      dict(color="#3B82F6", marker="+", linestyle="-", linewidth=1.8, markersize=5),
    "EPaxos":     dict(color="#1ABC9C", marker="^", linestyle="-", linewidth=1.8, markersize=5),
    "epaxos":     dict(color="#1ABC9C", marker="^", linestyle="-", linewidth=1.8, markersize=5),
    "FastPaxos":  dict(color="#0EA5E9", marker="o", linestyle="-", linewidth=1.8, markersize=5),
    "GPaxos":     dict(color="#6366F1", marker="s", linestyle="-", linewidth=1.8, markersize=5),
    "N2P":        dict(color="#16A34A", marker="v", linestyle="-", linewidth=1.8, markersize=5),
    "paxos":      dict(color="#000000", marker="o", linestyle="-", linewidth=1.5, markersize=4),
}

def load_proto_latency_cdf(path: str) -> ProtoCdf:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    result: ProtoCdf = {}
    for proto, pairs in data.items():
        result[proto] = [(float(x), float(y)) for x, y in pairs]
        result[proto].sort(key=lambda p: p[0])
    return result

def draw_cdf(
    cdf_data: Union[str, ProtoCdf],
    out_path: Optional[str] = None,
    title: Optional[str] = None,
    x_label: str = "latency (ms)",
    y_label: str = "CDF",
    xlim: Optional[Tuple[float, float]] = None,
    ylim: Tuple[float, float] = (0.0, 1.0),
    xticks: Optional[List[float]] = None,
    yticks: Optional[List[float]] = None,
    legend: bool = True,
    legend_loc: str = "lower right",
    grid: bool = True,
    vlines: Optional[List[Tuple[float, str]]] = None,  # [(x, label)]
    figsize: Tuple[float, float] = (6.2, 4.2),
    dpi: int = 200,
) -> None:
    if isinstance(cdf_data, str):
        data = load_proto_latency_cdf(cdf_data)
    else:
        data = {k: sorted([(float(x), float(y)) for x, y in v], key=lambda p: p[0])
                for k, v in cdf_data.items()}

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    for proto, points in data.items():
        if not points:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        style = PROTO_STYLE.get(proto, dict(marker="o", linestyle="-", linewidth=1.5, markersize=4))
        ax.plot(xs, ys, label=proto, **style)

    if grid:
        ax.grid(True, linestyle=":", alpha=0.4)
    if xlim:
        ax.set_xlim(*xlim)
    else:
        all_x = [x for pts in data.values() for x, _ in pts]
        if all_x:
            xmin, xmax = min(all_x), max(all_x)
            pad = 0.03 * (xmax - xmin) if xmax > xmin else 1.0
            ax.set_xlim(xmin - pad, xmax + pad)
    if ylim:
        ax.set_ylim(*ylim)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)

    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)
    else:
        ax.set_yticks(np.linspace(0, 1, 6))

    if vlines:
        for xv, lbl in vlines:
            ax.axvline(x=xv, color="#444", linestyle="-", alpha=0.6)
            if lbl:
                ax.text(xv, 1.0, f" {lbl}", rotation=90, va="top", ha="left", fontsize=9, color="#444")

    if legend:
        ax.legend(ncol=3, loc=legend_loc, fontsize=9, frameon=False)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()

if __name__ == "__main__":
    draw_cdf(
        cdf_data="out/proto_latency_cdf.yaml",
        out_path="out/latency_cdf.png",
        title="",
        xlim=(0, 5000),
        # xticks=list(range(100, 401, 50)),
        # vlines=[(200, "SLO 200ms"), (250, "Budget")],
        legend_loc="lower right",
    )