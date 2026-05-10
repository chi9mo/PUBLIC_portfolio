.PHONY: install run debug clean lint lint-strict build

install:
	python3 -m pip install --user --upgrade pip setuptools
	python3 -m pip install --user flake8 mypy build
	python3 -m pip install --user .
	@cd /tmp && apt-get download libxcb-keysyms1-dev 2>/dev/null && \
		dpkg-deb -x libxcb-keysyms1-dev_*.deb xcb-keysyms-dev && \
		rm -f libxcb-keysyms1-dev_*.deb
	tar xzf mlx_CLXV-2.2.tgz
	cd mlx_CLXV && touch config && make libmlx.so \
	CFLAGS="-I/tmp/xcb-keysyms-dev/usr/include -fPIC -Wall -O3 -I./src" \
	LDFLAGS="-L/tmp/xcb-keysyms-dev/usr/lib/x86_64-linux-gnu"
	cp mlx_CLXV/libmlx.so mlx_CLXV/python/src/mlx/
	python3 -m pip install --user mlx_CLXV/python/
	rm -rf mlx_CLXV/

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache build dist *.egg-info

lint: clean
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

lint-strict: clean
	flake8 .
	mypy . --strict

build:
	python3 -m build
	@cp dist/mazegen-*.whl . 2>/dev/null || true
	@cp dist/mazegen-*.tar.gz . 2>/dev/null || true
