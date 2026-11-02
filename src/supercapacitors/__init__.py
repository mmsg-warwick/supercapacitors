"""
Copyright (c) 2024 Ferran Brosa Planella. All rights reserved.

supercapacitors: A supercapacitors modelling project using PyBaMM
"""
__version__ = "0.1.0"

import pybamm

from supercapacitors.entry_point import Model, models, parameter_sets

__all__ = [
    "Model",
    "__version__",
    "models",
    "parameter_sets",
    "pybamm",
]
