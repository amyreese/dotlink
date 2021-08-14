srcs:=dotlink

build:
	flit build

dev:
	flit install --symlink

setup:
	python -m pip install -Ur requirements-dev.txt

.venv:
	python -m venv .venv
	source .venv/bin/activate && make setup dev
	echo 'run `source .venv/bin/activate` to use virtualenv'

venv: .venv

release: lint test clean
	flit publish

format:
	python -m ufmt format $(srcs)

lint:
	python -m flake8 $(srcs)
	python -m ufmt check $(srcs)

test:

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv