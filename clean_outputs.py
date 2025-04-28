from typing import List, Dict, TypedDict, Tuple, Literal, Optional
from config import ENCODING_EXP_OUTPUT_DIR, SCALING_EXP_OUTPUT_DIR, SPLICING_EXP_OUTPUT_DIR
import os
from pathlib import Path
import json
import pandas as pd
import numpy as np
from scipy.stats import gmean


class Phase(TypedDict):
    name: str
    path: str
    seconds: float
    count: int

SpackT = Literal["old-spack", "splice-spack"]
    
class Timer(TypedDict):
    total: float
    phases: List[Phase]

class FlatTimer(TypedDict):
    total: float
    setup: float
    load: float
    ground: float
    construct_specs: float
    solve: float

PHASES = ["setup", "load", "ground", "solve", "construct_specs", "total"]
CONFIGS = ["local", "remote"]

def flatten_timer(timer: Timer) -> FlatTimer:
    flat = FlatTimer({
        "total": timer["total"],
        "setup": 0.0,
        "load": 0.0,
        "ground": 0.0,
        "construct_specs": 0.0,
        "solve": 0.0
    }) 
    for phase in timer["phases"]:
        flat[phase['name']] = phase['seconds']
    
    return flat

def remove_spaces_from_spec_files(d: Path):
    for f in d.iterdir():
        new_name = f.name.replace(" ", "_")
        os.rename(str(f.absolute()), str(f.parent / new_name))
        

def parse_out_dir(path: Path):
    split_path = path.name.split("_")
    return split_path[0], "-".join(split_path[1:])

def load_json(file: Path):
    with open(file, "r") as f:
        return json.load(f)

def proc_out_dir(d: Path, branch: str, conf: str) -> pd.DataFrame:
    remove_spaces_from_spec_files(d)
    files_by_spec = {}
    for f in d.iterdir():
        spec_name = f.name.split("_")[0]
        specs = files_by_spec.setdefault(spec_name, [])
        specs.append(f)
    
    spec_dfs = []
    for spec, fs in files_by_spec.items():
        raw_data = pd.DataFrame([
            flatten_timer(load_json(f)["timer"])
            for f in fs if not f.is_dir()
        ])
        raw_data["spec"] = spec
        spec_dfs.append(raw_data)
    output_df = pd.concat(spec_dfs)
    output_df["spack"] = branch
    output_df["config"] = conf

    return output_df

def percentage_change(col1: pd.Series, col2: pd.Series):
    return col2.sub(col1).div(col1).mul(100)

def proc_all_outputs(output_root: Path) -> pd.DataFrame:
    clean_dfs = []
    for d in output_root.iterdir():
        branch, config = parse_out_dir(d)
        clean_dfs.append(proc_out_dir(d, branch, config))
    return pd.concat(clean_dfs).groupby(["spec", "spack", "config"], as_index=False)

def col_name_for_config(spack_ver: str, config_str: str):
    return f"{spack_ver}_{config_str}"

def comp_dfs_for_configs(mean_df: pd.DataFrame, phase: str):
    '''
    Useful for summary stats for splicing and scaling experiment
    '''
    small_df = mean_df[['spec', "spack", "config", phase]]
    small_df = small_df[small_df['spec']!="joint"]
    ndf = small_df.pivot_table(index='spec', columns=['spack', 'config'], values=phase)
    ndf.columns = [col_name_for_config(col[0], col[1]) for col in ndf.columns]
    ndf.reset_index(inplace=True)
    for conf in CONFIGS:
        try:
            old_col = ndf[col_name_for_config("old", conf)]
            new_col = ndf[col_name_for_config("splice", conf)]
            diff = percentage_change(old_col, new_col)
            ndf[f"{conf}_percent_diff"] = diff
        except KeyError as e:
            continue
    return ndf

def mean_increase_scaling_summary(mean_df):
    small_df = mean_df[['spec', 'config', 'total']]
    small_df = small_df[small_df['spec']!="joint"]
    ndf = small_df.pivot_table(index='spec', columns=['config'], values='total')
    ndf.reset_index(inplace=True)
    print(ndf)
    print(np.mean(percentage_change(ndf["many-10"], ndf["many-100"])))
    
def overall_average_summary(mean_df):
    comp_df = comp_dfs_for_configs(mean_df, "total")
    no_joint_df = comp_df[comp_df["spec"] != "joint"][["local_percent_diff", "remote_percent_diff"]]
    local_mean = np.mean(no_joint_df["local_percent_diff"])
    remote_mean = np.mean(no_joint_df["remote_percent_diff"])
    print(f"    Local Mean: {local_mean}")
    print(f"    Remote Mean: {remote_mean}")
    
if __name__ == "__main__":
    enc_mean_df = proc_all_outputs(ENCODING_EXP_OUTPUT_DIR).mean()
    splice_mean_df = proc_all_outputs(SPLICING_EXP_OUTPUT_DIR).mean()
    scaling_mean_df = proc_all_outputs(SCALING_EXP_OUTPUT_DIR).mean()
    print("Encoding")
    overall_average_summary(enc_mean_df)
    print("Splicing")
    overall_average_summary(splice_mean_df)
    print("Scaling")
    mean_increase_scaling_summary(scaling_mean_df)
