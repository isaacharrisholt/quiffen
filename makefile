PKG_NAME = 	quiffen

.PHONY:	test
test:
	( cd tests ; uv run pytest )

.PHONY:	lint
lint:
	( uv run ruff check $(PKG_NAME); uv run ruff check tests )

.PHONY:	wheel
wheel:
	uv build -f wheel

.PHONY:	install
install:	wheel
	uv sync

.PHONY:	reinstall
reinstall:	clean install

.PHONY:	clean
clean:
	find . -type d -name __pycache__ -prune -exec rm -r {} \;
	rm -fr build dist *.egg-info test2.qif
