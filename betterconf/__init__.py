"""Simple and very small Python library for configs. Doesn't have type-casts and other funcs, just parse env."""

from .config import Config
from .config import field, reference_field, compose_field, value, constant_field

__author__ = "prostomarkeloff"
