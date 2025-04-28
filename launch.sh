OLD_SPACK_BIN="./spacks/old-spack/bin/spack"
SPLICE_SPACK_BIN="./spacks/splice-spack/bin/spack"
OLD_SPACK_CONFIG_FILE="old-configs.jsonl"
SPLICE_SPACK_CONFIG_FILE="splice-configs.jsonl"
ENV_DIR="data/envs"

## TUNE THESE NUMBERS TO CHANGE RUNNING TIME
NPROCS=48 # Process level parallelism for each running experiments under configs
NRUNS=30 # How many identical runs for each config 

# Generate which configs do not have outputs
python generate.py --old-spack-config-file $OLD_SPACK_CONFIG_FILE \
       --new-spack-config-file $SPLICE_SPACK_CONFIG_FILE \
       --nruns $NRUNS \
       --encoding-exp \
       --splicing-exp \
       --scaling-exp

# Run all remaining configs for old spack
for ev in $ENV_DIR/*; do
    rm -rf ./cache/
    if [ -f "$ev/$OLD_SPACK_CONFIG_FILE" ]; then
        echo "$ev/$OLD_SPACK_CONFIG_FILE"
        $OLD_SPACK_BIN -e $ev python run_configs.py \
                       --config-file "$ev/$OLD_SPACK_CONFIG_FILE" \
                       --nprocs $NPROCS
    fi
done

# Run all remaining configs for new spack
for ev in $ENV_DIR/*; do
    rm -rf ./cache/
    if [ -f "$ev/$SPLICE_SPACK_CONFIG_FILE" ]; then
        echo "$ev/$SPLICE_SPACK_CONFIG_FILE"
        $SPLICE_SPACK_BIN -e $ev python run_configs.py \
                          --config-file "$ev/$SPLICE_SPACK_CONFIG_FILE" \
                          --nprocs $NPROCS
    fi
done
