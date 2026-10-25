"""Newtonian gravitational models for the 2D physics engine."""

from .newtonian import G, gravitational_accelerations
from .nbody import nbody_accelerations

__all__ = ["G", "gravitational_accelerations", "nbody_accelerations"]
