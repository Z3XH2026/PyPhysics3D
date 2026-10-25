"""Newtonian pairwise gravity calculations in SI-compatible units."""

import math

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D

G = 6.67430e-11


def gravitational_accelerations(
    body_a: Body2D,
    body_b: Body2D,
    gravitational_constant: float = G,
) -> tuple[Vector2, Vector2]:
    """Return accelerations on A and B caused by their mutual attraction.

    Positions are measured in metres, masses in kilograms, and the default G
    has SI units. Coincident positions are unsupported in this point-mass model.
    """
    if not math.isfinite(gravitational_constant) or gravitational_constant < 0:
        raise ValueError("gravitational_constant must be finite and non-negative")

    delta = body_b.position - body_a.position
    distance = delta.length()
    if distance == 0:
        raise ValueError("Bodies cannot occupy the same position")

    force_magnitude = (
        gravitational_constant * body_a.mass * body_b.mass / distance**2
    )
    force_a = delta / distance * force_magnitude
    force_b = force_a * -1

    return force_a / body_a.mass, force_b / body_b.mass
