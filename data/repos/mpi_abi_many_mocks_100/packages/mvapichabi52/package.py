# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import itertools
import os.path
import re
import sys

from spack.package import *



class Mvapichabi52(Package):
    """Mock of abi compatibility for mvapich"""

    homepage = "https://mvapich.cse.ohio-state.edu/userguide/userguide_spack/"
    url = "https://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich-3.0.tar.gz"
    list_url = "https://mvapich.cse.ohio-state.edu/downloads/"

    maintainers("natshineman", "harisubramoni", "MatthewLieber")

    executables = ["^mpiname$", "^mpichversion$"]

    license("Unlicense")

    # Prefer the latest stable release

    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated
    depends_on("fortran", type="build")  # generated

    provides("mpi")

    variant("wrapperrpath", default=True, description="Enable wrapper rpath")
    variant("debug", default=False, description="Enable debug info and error messages at run-time")

    variant("cuda", default=False, description="Enable CUDA extension")

    variant("regcache", default=True, description="Enable memory registration cache")

    # Accepted values are:
    #   single      - No threads (MPI_THREAD_SINGLE)
    #   funneled    - Only the main thread calls MPI (MPI_THREAD_FUNNELED)
    #   serialized  - User serializes calls to MPI (MPI_THREAD_SERIALIZED)
    #   multiple    - Fully multi-threaded (MPI_THREAD_MULTIPLE)
    #   runtime     - Alias to "multiple"
    variant(
        "threads",
        default="multiple",
        values=("single", "funneled", "serialized", "multiple"),
        multi=False,
        description="Control the level of thread support",
    )

    # 32 is needed when job size exceeds 32768 cores
    variant(
        "ch3_rank_bits",
        default="32",
        values=("16", "32"),
        multi=False,
        description="Number of bits allocated to the rank field (16 or 32)",
    )
    variant(
        "pmi_version",
        description="Which pmi version to be used. If using pmi2 add it to your CFLAGS",
        default="simple",
        values=("simple", "pmi2"),
        multi=False,
    )

    variant(
        "process_managers",
        description="List of the process managers to activate",
        values=disjoint_sets(("auto",), ("slurm",), ("hydra", "gforker", "remshell"))
        .with_error("'slurm' or 'auto' cannot be activated along with " "other process managers")
        .with_default("auto")
        .with_non_feature_values("auto"),
    )

    variant(
        "netmod",
        description="Select the netmod to be enabled for this build."
        "For IB/RoCE systems, use the ucx netmod, for interconnects supported "
        "by libfabrics, use the ofi netmod. For more info, visit the "
        "homepage url.",
        default="ofi",
        values=("ofi", "ucx"),
        multi=False,
    )

    variant(
        "alloca", default=False, description="Use alloca to allocate temporary memory if available"
    )

    variant(
        "file_systems",
        description="List of the ROMIO file systems to activate",
        values=auto_or_any_combination_of("lustre", "gpfs", "nfs", "ufs"),
    )

    depends_on("findutils", type="build")
    depends_on("bison", type="build")
    depends_on("pkgconfig", type="build")
    depends_on("zlib-api")
    depends_on("libpciaccess", when=(sys.platform != "darwin"))
    depends_on("libxml2")
    depends_on("cuda", when="+cuda")
    depends_on("libfabric", when="netmod=ofi")
    depends_on("slurm", when="process_managers=slurm")
    depends_on("ucx", when="netmod=ucx")

    with when("process_managers=slurm"):
        conflicts("pmi_version=pmi2")

    with when("process_managers=auto"):
        conflicts("pmi_version=pmi2")

    filter_compiler_wrappers("mpicc", "mpicxx", "mpif77", "mpif90", "mpifort", relative_root="bin")


    version('3.0')
    can_splice('mpich@3.4.3', when='@3.0')
