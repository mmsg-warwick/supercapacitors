"""
Copyright (c) 2024 Ferran Brosa Planella. All rights reserved.

supercapacitors: A supercapacitors modelling project using PyBaMM
"""
__version__ = "0.1.0"

import pybamm
from supercapacitors.entry_point import Model, parameter_sets, models

__all__ = [
    "__version__",
    "pybamm",
    "parameter_sets",
    "Model",
    "models",
]
