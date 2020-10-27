py := poetry run

install:
	pip install poetry
	poetry install

black:
	$(py) black betterconf/

pre-commit:
	$(py) pre-commit install

mypy:
	$(py) mypy betterconf/
