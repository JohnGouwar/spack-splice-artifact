from pathlib import Path
from typing import TypedDict, Any, Sequence, Mapping
import json
import os
# These strings are Paths, but serializing paths to JSON is not supported
# directly 
class ExpConfig(TypedDict):
    specs: list[str]
    env: str
    result_file: str

EXP_ROOT = Path(os.getcwd())
SPACK_ROOT = EXP_ROOT / "spacks"
OLD_SPACK = SPACK_ROOT / "old-spack"
NEW_SPACK = SPACK_ROOT / "splice-spack"
DATA_DIR = EXP_ROOT / "data"
ENV_DIR = DATA_DIR / "envs"
REPO_DIR = DATA_DIR / "repos"
BUILDCACHE_ENV = DATA_DIR / "radiuss-mirror"
OUTPUT_DIR = DATA_DIR / "outputs"
ENCODING_EXP_OUTPUT_DIR = OUTPUT_DIR / "encoding"
SPLICING_EXP_OUTPUT_DIR = OUTPUT_DIR / "splicing"
SCALING_EXP_OUTPUT_DIR = OUTPUT_DIR / "scaling"
CACHE_CONFIGS = ["local", "remote"]
# $ spack list -t RADIUSS | sed 's/.*/"&",/' | cat
RADIUSS_SPECS = [
    "aluminum",
    "ascent",
    "axom",
    "blt",
    "caliper",
    "care",
    "chai+mpi",
    "conduit",
    "dihydrogen",
    "flux-core",
    "flux-sched",
    "flux-security",
    "glvis ^mfem+mpi",
    "hiptt",
    "hydrogen",
    "hypre",
    "lbann",
    "lvarray+chai",
    "mfem+mpi",
    "py-hatchet",
    "py-maestrowf",
    "py-merlin",
    "py-shroud",
    "raja",
    "raja-perf+mpi",
    "samrai",
    "scr",
    "sundials+mpi",
    "umpire+mpi",
    "visit+mpi",
    "xbraid",
    "zfp",   
]
# Manually checked for an MPI dependency 
MPI_RADIUSS_SPECS = [
    "aluminum",
    "ascent",
    "axom",
    "caliper",
    "chai+mpi",
    "conduit",
    "dihydrogen",
    "hydrogen",
    "hypre",
    "lbann",
    "lvarray+chai",
    "mfem+mpi",
    "glvis ^mfem+mpi",
    "raja-perf+mpi",
    "samrai",
    "scr",
    "sundials+mpi",
    "umpire+mpi",
    "visit+mpi",
    "xbraid",
]

def read_jsonl_stream(file: Path):
    with open(file, "r") as f:
        for line in f:
            if not line.isspace():
                yield json.loads(line)

def write_jsonl(data: Sequence[Mapping[str, Any]], file: Path):
    text = [json.dumps(d) for d in data]
    with open(file, "a") as f:
        f.write("\n".join(text))
        f.write("\n")

def get_index_from_jsonl(file: Path, index: int):
    for (i, record) in enumerate(read_jsonl_stream(file)):
        if i == index:
            return record
    raise Exception(f"Failed to get index: {index} from {file}")
