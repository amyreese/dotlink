srcs:=dotlink

.venv:
	python -m venv .venv
	source .venv/bin/activate && make install
	echo 'run `source .venv/bin/activate` to use virtualenv'

venv: .venv

install:
	python -m pip install -U pip
	python -m pip install -Ue .[dev]

release: lint test clean
	flit publish

format:
	python -m ufmt format $(srcs)

test:
	python -m pytest
	python -m mypy --non-interactive --install-types -p $(srcs)

lint:
	python -m flake8 $(srcs)
	python -m ufmt check $(srcs)

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv