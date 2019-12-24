black:
	black betterconf/

install:
	pip install poetry
	poetry install

pre-commit:
	pre-commit install

mypy:
	mypy betterconf/
