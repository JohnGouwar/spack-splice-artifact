from typing import List, Tuple
from pathlib import Path
from config import (
    ENCODING_EXP_OUTPUT_DIR,
    SCALING_EXP_OUTPUT_DIR,
    SPLICING_EXP_OUTPUT_DIR,
    ENV_DIR,
    MPI_RADIUSS_SPECS,
    RADIUSS_SPECS,
    CACHE_CONFIGS,
    ExpConfig,
    write_jsonl
)
from argparse import ArgumentParser 

def clap():
    parser = ArgumentParser()
    parser.add_argument(
        "--nruns",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--old-spack-config-file",
        type=str,
        required=True
    )
    parser.add_argument(
        "--new-spack-config-file",
        type=str,
        required=True
    )
    parser.add_argument(
        "--encoding-exp",
        action="store_true"
    )
    parser.add_argument(
        "--splicing-exp",
        action="store_true",
    )
    parser.add_argument(
        "--scaling-exp",
        action="store_true"
    )
    return parser.parse_args()

def _gen_configs_for_specs(
        nruns: int,
        specs: List[str],
        env: Path,
        cache_config: str,
        config_file_name: str,
        exp_output_dir: Path,
        spack_ver: str
):
    experiment_configs = []
    config_output_dir = exp_output_dir / f"{spack_ver}_{cache_config}"
    config_output_dir.mkdir(exist_ok=True, parents=True)
    for i in range(nruns):
        for spec in specs:
            spec_result_file = config_output_dir / f"{spec}_{i}.json"
            if spec_result_file.exists():
                continue
            cfg = ExpConfig(
                specs=[spec],
                env=str(env),
                result_file=str(spec_result_file)
            )
            experiment_configs.append(cfg)
        
        joint_result_file = config_output_dir / f"joint_{i}.json"
        if joint_result_file.exists():
            continue
        joint_config = ExpConfig(
            specs=RADIUSS_SPECS,
            env = str(env),
            result_file=str(joint_result_file)
        )
        experiment_configs.append(joint_config)
    
    write_jsonl(experiment_configs, env / config_file_name)

def gen_configs_for_encoding_experiment(
        nruns: int,
        old_config_file_name: str,
        new_config_file_name: str 
):
    """
    Generate configs for the first experiment which compares the performance of
    the old encoding to the new encoding

    Args:
      nruns: the number of runs per config 
    """
    
    ENCODING_EXP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cache_config in CACHE_CONFIGS:
        env = ENV_DIR / f"no-splice_{cache_config}"
        _gen_configs_for_specs(
            nruns,
            RADIUSS_SPECS,
            env,
            cache_config,
            old_config_file_name,
            ENCODING_EXP_OUTPUT_DIR,
            "old"
        )
        _gen_configs_for_specs(
            nruns,
            RADIUSS_SPECS,
            env,
            cache_config,
            new_config_file_name,
            ENCODING_EXP_OUTPUT_DIR,
            "splice"
        ) 
                    
def gen_configs_for_splicing_experiment(
        nruns: int,
        old_config_file_name: str,
        new_config_file_name: str
):
    """
    Generate configs for the second experiment which compares the performance of
    old spack to spliced spack

    Args:
      output_dir: the output directory for each run (relative to EXP_ROOT)
      nruns: the number of runs per config 
    """
    SPLICING_EXP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    old_specs = [s + " ^mpich" for s in MPI_RADIUSS_SPECS] + ["py-shroud"]
    new_specs = [s + " ^mvapichabi0" for s in MPI_RADIUSS_SPECS] + ["py-shroud"]
    for cache_config in CACHE_CONFIGS:
        old_env = ENV_DIR / f"no-splice_{cache_config}"
        new_env = ENV_DIR / f"splice_{cache_config}"
        _gen_configs_for_specs(
            nruns,
            old_specs,
            old_env,
            cache_config,
            old_config_file_name,
            SPLICING_EXP_OUTPUT_DIR,
            "old"
        )
        _gen_configs_for_specs(
            nruns,
            new_specs,
            new_env,
            cache_config,
            new_config_file_name,
            SPLICING_EXP_OUTPUT_DIR,
            "splice"
        )

def gen_configs_for_scaling_experiment(nruns: int, new_config_filename: str):
    exp_configs = []
    SCALING_EXP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for env in ENV_DIR.iterdir():
        if not env.name.startswith("many"):
            continue
        _gen_configs_for_specs(
            nruns,
            RADIUSS_SPECS,
            env,
            env.name,
            new_config_filename,
            SCALING_EXP_OUTPUT_DIR,
            "splice"
        )

if __name__ == "__main__":
    args = clap()
    if args.encoding_exp:
        gen_configs_for_encoding_experiment(
            args.nruns,
            args.old_spack_config_file,
            args.new_spack_config_file
        )
    if args.splicing_exp:
        gen_configs_for_splicing_experiment(
            args.nruns,
            args.old_spack_config_file,
            args.new_spack_config_file
        )
    if args.scaling_exp:
        gen_configs_for_scaling_experiment(args.nruns, args.new_spack_config_file)
    
