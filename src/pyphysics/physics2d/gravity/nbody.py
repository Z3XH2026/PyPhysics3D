"""Direct O(N²) gravitational acceleration summation."""

from collections.abc import Sequence
import math

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from .newtonian import G, gravitational_accelerations


def nbody_accelerations(
    bodies: Sequence[Body2D],
    gravitational_constant: float = G,
) -> list[Vector2]:
    """Return net gravitational acceleration for each body, in input order.

    Does not modify positions or velocities. Every unique pair is computed
    once. Coincident positions are unsupported in this point-mass model.
    """
    if not math.isfinite(gravitational_constant) or gravitational_constant < 0:
        raise ValueError("gravitational_constant must be finite and non-negative")

    accelerations = [Vector2(0.0, 0.0) for _ in bodies]

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            accel_i, accel_j = gravitational_accelerations(
                bodies[i], bodies[j], gravitational_constant
            )
            accelerations[i] = accelerations[i] + accel_i
            accelerations[j] = accelerations[j] + accel_j

    return accelerations
