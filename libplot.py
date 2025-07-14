import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, TypedDict, Tuple, Literal, Optional
from matplotlib.axes import Axes


def plot_grouped_boxes(
        data: Dict[str, Dict[str, List[float]]],
        specs: List[str],
        ax: Axes,
):
    """
    data: maps box labels to a map of specs to times for a phase
    """
    flat_data = [0, 0]
    for i, (lab, vals) in enumerate(data.items()):
        if lab == "Old Spack":
            flat_data[0] = (lab, (f"C{0}", [vals[s.split()[0]] for s in specs]))
        elif lab == "Splice Spack":
            flat_data[1] = (lab, (f"C{1}", [vals[s.split()[0]] for s in specs]))
    flat_data = [d for d in flat_data if d != 0]
    multiplier = 1
    NUM_LABELS = 3 
    for i, (label, (color, vals)) in enumerate(flat_data):
        posns_subset = [0.1 + i/NUM_LABELS + j for j in range(len(vals))]
        ax.boxplot(
            vals,
            positions=posns_subset,
            label=label,
            widths=0.2,
            patch_artist=True,
            boxprops=dict(facecolor=color),
            showfliers=False,
            medianprops=dict(color="black")
        )
        multiplier+=1
    spec_ticks = np.arange(len(specs)) + 0.325
    ax.set_xticks(spec_ticks, specs)
    # line_ticks = np.arange(len(specs)) - 0.125
    # for tick in line_ticks:
    #     ax.axvline(x = tick, color="b")


def plot_stacked_lines(
        xs : list,
        data: List[Tuple[str, List[float]]],
        ax: Axes
):
    patterns = ["-o", "-x", "-s", "-v", "-p"]
    for (i, (s, vals)) in enumerate(data):
        ax.plot(xs, vals, patterns[i % len(patterns)], label=s)
