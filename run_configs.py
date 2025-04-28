from multiprocessing import Pool
from argparse import ArgumentParser
from pathlib import Path
from spack.environment import Environment, activate, deactivate 
from spack.stage import tempfile
from spack.util.timer import Timer
import spack.solver.asp
import spack.config
from spack.spec import Spec
from typing import List
import json

def read_jsonl_stream(file: Path):
    with open(file, "r") as f:
        for line in f:
            if not line.isspace():
                yield json.loads(line)

def _solve_specs_timed(specs: List[Spec]) -> Timer:
    solver = spack.solver.asp.Solver()
    _, timer, _ = solver.solve_with_stats(specs)
    assert isinstance(timer, Timer)
    return timer

def time_config(conf):
    try:
        specs = [Spec(s) for s in conf["specs"]]
        output = {
            "specs": conf["specs"],
            "timer": _solve_specs_timed(specs).write_json(out=False),
            "env": conf['env']
        }
        return (output, conf['result_file'])
    except Exception as ex:
        return (ex, conf['result_file'])

def clap():
    parser = ArgumentParser()
    parser.add_argument("--config-file", type=Path, required=True)
    parser.add_argument("--nprocs", type=int, required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = clap()
    configs = read_jsonl_stream(args.config_file)
    # for conf in configs:
    #     output, file = time_config(conf)
    #     if isinstance (output, Exception):
    #         filename = file+".err"
    #         with open(filename, "w") as f:
    #             f.write(str(output))
    #     else:
    #         with open(file, "w") as f:
    #             json.dump(output, f)
    with Pool(args.nprocs) as p:
        for (output, file) in p.imap_unordered(
                time_config,
                configs,
        ):
            if isinstance (output, Exception):
                filename = file+".err"
                with open(filename, "w") as f:
                    f.write(str(output))
            else:
                with open(file, "w") as f:
                    json.dump(output, f)
        
    
