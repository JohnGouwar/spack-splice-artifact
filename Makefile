spacks:
	./clone_spacks.sh

buildcache: spacks
	./spacks/old-spack/bin/spack python make_mock_buildcache.py --env data/radiuss-mirror

experiments: buildcache
	./launch.sh

plots:
	python plots.py

clean:
	rm -rf data/outputs
	./clean_configs.sh

all: experiments plots

