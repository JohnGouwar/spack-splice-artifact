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
    flat_data = [0, 0, 0, 0]
    for i, (lab, vals) in enumerate(data.items()):
        if lab == "Old Spack + local BC":
            print(0)
            flat_data[0] = (lab, (f"C{i}", [vals[s] for s in specs]))
        elif lab == "Splice Spack + local BC":
            print(1)
            flat_data[1] = (lab, (f"C{i}", [vals[s] for s in specs]))
        elif lab == "Old Spack + public BC":
            print(2)
            flat_data[2] = (lab, (f"C{i}", [vals[s] for s in specs]))
        elif lab == "Splice Spack + public BC":
            print(3)
            flat_data[3] = (lab, (f"C{i}", [vals[s] for s in specs]))
        
    multiplier = 1
    NUM_LABELS= 4 
    for i, (label, (color, vals)) in enumerate(flat_data):
        posns_subset = [i/NUM_LABELS + j for j in range(len(vals))]
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
    spec_ticks = np.arange(len(specs)) + 0.375
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
        ax.plot(xs, vals, patterns[i], label=s)
