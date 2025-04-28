ENV_DIR="data/envs"

for ev in $ENV_DIR/*; do
    pushd $ev
    rm -f *.jsonl
    popd
done
