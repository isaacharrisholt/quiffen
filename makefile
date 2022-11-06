PKG_NAME = 	quiffen

.PHONY:		test
test:
		( cd tests ; poetry run pytest )

.PHONY:     lint
lint:
        ( poetry run pylint $(PKG_NAME); poetry run pylint tests )

.PHONY:		wheel
wheel:
		poetry build -f wheel

.PHONY:		install
install:	wheel
		poetry install

.PHONY:		reinstall
reinstall:	clean install

.PHONY:		clean
clean:
		find . -type d -name __pycache__ -prune -exec rm -r {} \;
		rm -fr build dist *.egg-info test2.qif
