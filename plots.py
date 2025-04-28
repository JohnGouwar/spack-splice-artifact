from libplot import plot_grouped_boxes, plot_stacked_lines
from config import ENCODING_EXP_OUTPUT_DIR, SCALING_EXP_OUTPUT_DIR, SPLICING_EXP_OUTPUT_DIR
from clean_outputs import proc_all_outputs
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

def dfs_to_boxplot_data(exp_output_path: Path):
    dfs = proc_all_outputs(exp_output_path)
    plot_data = {}
    for df in dfs:
        spec, spack_ver, config = df[0]
        if "+" in spec:
            spec = spec.split("+")[0]
        total_times = np.array(df[1]['total'])
        build_cache_config = "public" if config == "remote" else "local"
        if spack_ver == "old":
            key = f"Old Spack + {build_cache_config} BC"
        else:
            key = f"Splice Spack + {build_cache_config} BC"
        plot_data.setdefault(key, {})
        plot_data[key][spec] = list(total_times)
    return plot_data

def dfs_to_scaling_data(exp_output_path, select_specs):
    dfs = proc_all_outputs(exp_output_path).mean()
    data = []
    for df in dfs.groupby(['spec']):
        spec = df[0][0]
        if "+" in spec:
            spec = spec.split("+")[0]
        if spec not in select_specs:
            continue
        conf_time_tups = [
            (int(t[0].split('-')[-1]), t[1])
            for t in list(df[1][['config', 'total']].itertuples(index=False, name=None))
        ]
        conf_time_tups.sort(key=lambda x: x[0])
        data.append((spec, [t[1] for t in conf_time_tups]))
    return data

def encoding_total_plot(figpath: Path):
    plot_data = dfs_to_boxplot_data(ENCODING_EXP_OUTPUT_DIR)
    fig, axes = plt.subplots(figsize=(4,3))
    SELECT_ENCODING_SPECS = ["py-shroud", "caliper", "mfem",  "joint"]
    plot_grouped_boxes(plot_data, SELECT_ENCODING_SPECS, axes)
    axes.legend(loc="upper left", fontsize="small", frameon=False)
    axes.set_xlabel("Concretization goal")
    axes.set_ylabel("Concretization time (s)")
    fig.tight_layout()
    fig.savefig(str(figpath), bbox_inches="tight")
    
def splicing_total_plot(figpath: Path):
    plot_data = dfs_to_boxplot_data(SPLICING_EXP_OUTPUT_DIR)
    fig, axes = plt.subplots(figsize=(4,3))
    SELECT_SPLICING_SPECS = ["py-shroud", "caliper", "mfem", "joint"]
    plot_grouped_boxes(plot_data, SELECT_SPLICING_SPECS, axes)
    axes.legend(loc="upper left", fontsize="small", frameon=False)
    axes.set_xlabel("Concretization goal")
    axes.set_ylabel("Concretization time (s)")
    fig.tight_layout()
    fig.savefig(str(figpath))

def scaling_line_plot(figpath: Path):
    SELECT_SCALING_SPECS = ["py-shroud", "caliper", "mfem",  "joint"]
    plot_data = dfs_to_scaling_data(SCALING_EXP_OUTPUT_DIR, SELECT_SCALING_SPECS)
    fig, axes = plt.subplots(figsize=(4,3))
    xs = list(range(10, 110, 10))
    plot_stacked_lines(xs, plot_data, axes)
    axes.legend(loc="upper left", fontsize="small", frameon=False)
    axes.set_xlabel("Number of mpiabi replicas")
    axes.set_ylabel("Concretization time (s)")
    fig.tight_layout()
    fig.savefig(str(figpath))

if __name__ == "__main__":
    fig_root = Path("figures")
    encoding_total_plot(fig_root / "encoding.png")
    splicing_total_plot(fig_root / "splicing.png")
    scaling_line_plot(fig_root / "scaling.png")
    
