install: .venv
	/Users/butterkeks/anaconda3/envs/globus_index/bin/python setup.py -q develop
	rm -f searchable-files
	ln -s "/Users/butterkeks/anaconda3/envs/globus_index/bin/searchable-files" searchable-files

lint:
	pre-commit run -a

.venv:
	virtualenv --python=python3 /Users/butterkeks/anaconda3/envs/globus_index/
	/Users/butterkeks/anaconda3/envs/globus_index/bin/python -m pip install -q -U pip setuptools

clean:
	find -name '*.pyc' -delete
	rm -f searchable-files
	rm -rf .venv
	rm -rf dist
	rm -rf src/*.egg-info
