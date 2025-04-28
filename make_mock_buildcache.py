from argparse import ArgumentParser
from spack.environment import Environment, activate
import spack.binary_distribution as bindist
from spack.cmd.common import arguments
from pathlib import Path
from spack import traverse
import spack.deptypes as dt
from typing import List
import json
import os

from spack.mirror import Mirror
from spack.spec import Spec

def clap():
    parser = ArgumentParser()
    parser.add_argument(
        "--env",
        type=str,
        help="The environment to concretize and mock a buildcache from"
    )
    
    return parser.parse_args()

def from_env(env_path: str):
    env = Environment(env_path)
    cache_dir = Path(env_path) / "cache"
    if cache_dir.exists():
        return 
    cache_dir.mkdir()
    mock_mirror = Mirror(str(cache_dir))
    activate(env)
    env.concretize(force=True)
    env.install_all(fake=True)
    all_specs_to_push = [
        s
        for s in traverse.traverse_nodes(
                env.concrete_roots(),
                root=True,
                deptype=(dt.RUN | dt.LINK | dt.TEST),
                order="breadth",
                key=traverse.by_dag_hash
        )
        if not s.external
    ]
    all_specs_to_push.reverse()
    with bindist.make_uploader(
            mirror=mock_mirror,
            force=True,
            update_index=True,
            signing_key=None
    ) as uploader:
        skipped, upload_errors = uploader.push(all_specs_to_push)

if __name__  == "__main__":
    args = clap()
    if args.env:
        from_env(args.env)
