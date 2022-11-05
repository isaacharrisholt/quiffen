PKG_NAME = 	quiffen
PY_BIN = 	python

.PHONY:		test
test:
		( cd tests ; poetry run pytest )

.PHONY:		wheel
wheel:
		$(PY_BIN) setup.py bdist_wheel --universal

.PHONY:		install
install:	wheel
		$(PY_BIN) -m pip install --force-reinstall dist/$(PKG_NAME)-*.whl

.PHONY:		reinstall
reinstall:	clean install

.PHONY:		clean
clean:
		find . -type d -name __pycache__ -prune -exec rm -r {} \;
		rm -fr build dist *.egg-info test2.qif


# TODO: makefile edits