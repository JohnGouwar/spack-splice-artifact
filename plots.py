from functools import reduce
from src.viz.libplot import plot_grouped_boxes, plot_stacked_lines
from src.boa.config import ENCODING_EXP_OUTPUT_DIR, RADIUSS_SPECS, SCALING_EXP_OUTPUT_DIR, SPLICING_EXP_OUTPUT_DIR
from src.proc.clean_outputs import proc_all_outputs
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
#FIG_SIZE = (6.4, 5.8)
FIG_SIZE = (16, 9)
SPEC_ROTATION = 45
AXIS_FONTSIZE = 12
CLEAN_RADIUSS_SPECS = [
    "aluminum",
    "ascent",
    "axom",
    "blt",
    "caliper",
    "care",
    "chai",
    "conduit",
    "dihydrogen",
    "flux-core",
    "flux-sched",
    "flux-security",
    "glvis",
    "hiptt",
    "hydrogen",
    "hypre",
    "lbann",
    "lvarray",
    "mfem",
    "py-hatchet",
    "py-maestrowf",
    "py-merlin",
    "py-shroud",
    "raja",
    "raja-perf",
    "samrai",
    "scr",
    "sundials",
    "umpire",
    "visit",
    "xbraid",
    "zfp",   
]
CLEAN_MPI_RADIUSS_SPECS = [
      "py-shroud",
      "aluminum",
      "ascent",
      "axom",
      "caliper",
      "care",
      "chai",
      "conduit",
      "dihydrogen",
      "hydrogen",
      "hypre",
      "lbann",
      "lvarray",
      "mfem",
      "glvis",
      "raja-perf",
      "samrai",
      "scr",
      "sundials",
      "umpire",
      "visit",
      "xbraid",
]
CLEAN_RADIUSS_SPECS_TICKS = [
    "aluminum (434)",
    "ascent (685)",
    "axom (676)",
    "blt (357)",
    "caliper (444)",
    "care (364)",
    "chai (363)",
    "conduit (460)",
    "dihydrogen (501)",
    "flux-core (395)",
    "flux-sched (397)",
    "flux-security (72)",
    "glvis (678)",
    "hiptt (357)",
    "hydrogen (437)",
    "hypre (464)",
    "lbann (726)",
    "lvarray (453)",
    "mfem (676)",
    "py-hatchet (520)",
    "py-maestrowf (123)",
    "py-merlin (435)",
    "py-shroud (65)",
    "raja (361)",
    "raja-perf (448)",
    "samrai (358)",
    "scr (407)",
    "sundials (595)",
    "umpire (359)",
    "visit (687)",
    "xbraid (357)",
    "zfp (357)"
]
CLEAN_MPI_RADIUSS_SPECS_TICKS = [
    "aluminum (434)",
    "ascent (685)",
    "axom (676)",
    "caliper (444)",
    "chai (363)",
    "conduit (460)",
    "dihydrogen (501)",
    "glvis (678)",
    "hydrogen (437)",
    "hypre (464)",
    "lbann (726)",
    "lvarray (453)",
    "mfem (676)",
    "py-shroud (65)",
    "raja-perf (448)",
    "samrai (358)",
    "scr (407)",
    "sundials (595)",
    "umpire (359)",
    "visit (687)",
    "xbraid (357)"
]

def dfs_to_rebuttal_boxplot_data(exp_output_path: Path):
    """
    Returns a top and bottom boxplot
    """
    dfs = proc_all_outputs(exp_output_path)
    plot_data = {"top": {} , "bottom": {}}
    for df in dfs:
        spec, spack_ver, config = df[0]
        if "+" in spec:
            spec = spec.split("+")[0]
        total_times = np.array(df[1]['total'])
        build_cache_config = "public" if config == "remote" else "local"
        if build_cache_config == "public":
            data = plot_data["bottom"]
        else:
            data = plot_data["top"]
        if spack_ver == "old":
            key = f"Old Spack"
        else:
            key = f"Splice Spack"
        data.setdefault(key, {})
        data[key][spec] = list(total_times)
    return plot_data

def dfs_to_rebut_scaling_data(exp_output_path, select_specs, filter_confs):
    def _spec_cleaner(s):
        if "+" in s:
            return s.split("+")[0]
        else:
            return s
    dfs = proc_all_outputs(exp_output_path).mean()
    def _key(s):
        conf_df = dfs[dfs['config'] == 'many-10']
        conf_df['spec'] = conf_df['spec'].map(_spec_cleaner)
        return conf_df[conf_df['spec'] == s]['total'].iat[0]
    sorted_specs = sorted(select_specs, key=_key)
    data = []
    for (conf_tup, df) in dfs.groupby(['config']):
        conf_num = int(conf_tup[0].split("-")[-1])
        df['spec'] = df['spec'].map(_spec_cleaner)
        data_for_conf = [
            df[df['spec'] == s]['total'].iat[0]
            for s in sorted_specs
        ]
        data.append((conf_num, data_for_conf))
    data.sort(key=lambda x: x[0])
    return (
        [(f"{conf} mpiabi replicas", vs) for (conf, vs) in data if conf in filter_confs],
        sorted_specs
    )

def specs_sorted_by_mean(specs, data, key):
    def _key_fn(spec):
        return int(np.mean(data[key][spec.split()[0]]))
    return sorted(specs, key=_key_fn)
    
def rebut_encoding_plot(figpath: Path):
    plot_data = dfs_to_rebuttal_boxplot_data(ENCODING_EXP_OUTPUT_DIR)
    fig, axes = plt.subplots(2, figsize=FIG_SIZE, layout="constrained")
    sorted_specs = specs_sorted_by_mean(CLEAN_RADIUSS_SPECS_TICKS, plot_data["top"], "Old Spack")
    plot_grouped_boxes(plot_data["top"], sorted_specs, axes[0])
    plot_grouped_boxes(plot_data["bottom"], sorted_specs, axes[1])
    axes[0].legend(loc="upper left", fontsize="small", frameon=False)
    axes[0].set_title("Access to local buildcache")
    axes[1].set_title("Access to remote buildcache")
    fig.supxlabel("Concretized spec (\\# of possible dependencies)", fontsize=AXIS_FONTSIZE)
    fig.supylabel("Concretization time (s)", fontsize=AXIS_FONTSIZE)
    axes[0].set_xticks(axes[0].get_xticks(), [])
    axes[1].set_xticks(
        axes[1].get_xticks(),
        axes[1].get_xticklabels(),
        rotation=SPEC_ROTATION,
        ha="right",
        rotation_mode="anchor"
    ) 
    fig.savefig(str(figpath), bbox_inches="tight")
    
def rebut_splicing_plot(figpath: Path):
    plot_data = dfs_to_rebuttal_boxplot_data(SPLICING_EXP_OUTPUT_DIR)
    fig, axes = plt.subplots(2, figsize=FIG_SIZE, layout="constrained")
    sorted_specs = specs_sorted_by_mean(CLEAN_MPI_RADIUSS_SPECS_TICKS, plot_data["top"], "Old Spack")
    plot_grouped_boxes(plot_data["top"], sorted_specs, axes[0])
    plot_grouped_boxes(plot_data["bottom"], sorted_specs, axes[1])
    axes[0].legend(loc="upper left", fontsize="small", frameon=False)
    axes[0].set_title("Access to local buildcache")
    axes[1].set_title("Access to remote buildcache")
    fig.supxlabel("Concretized spec (\\# of possible dependencies)", fontsize=AXIS_FONTSIZE)
    fig.supylabel("Concretization time (s)", fontsize=AXIS_FONTSIZE)
    axes[0].set_xticks(axes[0].get_xticks(), [])
    axes[1].set_xticks(
        axes[1].get_xticks(),
        axes[1].get_xticklabels(),
        rotation=SPEC_ROTATION,
        ha="right",
        rotation_mode="anchor"
    ) 
    fig.savefig(str(figpath), bbox_inches="tight")

def rebut_scaling_plot(figpath: Path):
    (plot_data, sorted_specs) = dfs_to_rebut_scaling_data(
        SCALING_EXP_OUTPUT_DIR,
        CLEAN_RADIUSS_SPECS,
        [10, 50, 100]
    )
    bar_width = 0.2
    multiplier = 0
    xs = np.arange(len(CLEAN_RADIUSS_SPECS))
    fig, ax = plt.subplots(figsize=(6.4, 3.2), layout="constrained")
    for (conf, val) in plot_data:
        offset = bar_width * multiplier
        ax.bar(xs + offset, val, bar_width, label=conf)
        multiplier += 1
    ax.legend(loc="upper left", fontsize="small", frameon=False)
    ax.set_ylabel("Mean concretization time (s)", fontsize=AXIS_FONTSIZE)
    ticks = [
        f"{s}*" if s != "py-shroud" and s in CLEAN_MPI_RADIUSS_SPECS else s
        for s in sorted_specs
    ]
    ax.set_xticks(xs+bar_width, ticks)
    ax.set_xlabel("Concretized spec (* indicates MPI dependency)", fontsize=AXIS_FONTSIZE)
    ax.set_ylim([0, 95])
    ax.set_xticks(
        ax.get_xticks(),
        ax.get_xticklabels(),
        rotation=SPEC_ROTATION,
        ha="right",
        rotation_mode="anchor"
    ) 
    fig.savefig(str(figpath), bbox_inches="tight")
    
if __name__ == "__main__":
    fig_root = Path("figures")
    fig_root.mkdir(exist_ok=True)
    rebut_encoding_plot(fig_root / "figure5.png")
    rebut_splicing_plot(fig_root / "figure6.png")
    rebut_scaling_plot(fig_root / "figure7.png")
    
