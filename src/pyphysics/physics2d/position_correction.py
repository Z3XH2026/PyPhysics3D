"""Mass-weighted positional correction for overlapping 2D circles.

Place this module in src/pyphysics/physics2d/position_correction.py.
This only corrects positions; collision impulses are handled separately.
"""

from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.contact import collision_normal


def correct_circle_positions(
    body_a: Body2D,
    radius_a: float,
    body_b: Body2D,
    radius_b: float,
) -> bool:
    """Separate overlapping circles along their center-to-center normal.

    Move lighter bodies farther using inverse-mass weighting.
    Return True if a correction was applied, otherwise False.
    """
    if radius_a <= 0 or radius_b <= 0:
        raise ValueError("Circle radii must be positive")

    delta = body_b.position - body_a.position
    distance = delta.length()
    penetration = radius_a + radius_b - distance

    if penetration <= 0:
        return False

    # The existing collision_normal() uses (1, 0) if centers coincide.
    normal = collision_normal(body_a.position, body_b.position)

    inverse_mass_a = 1.0 / body_a.mass
    inverse_mass_b = 1.0 / body_b.mass
    inverse_mass_sum = inverse_mass_a + inverse_mass_b

    move_a = penetration * inverse_mass_a / inverse_mass_sum
    move_b = penetration * inverse_mass_b / inverse_mass_sum

    body_a.position = body_a.position - normal * move_a
    body_b.position = body_b.position + normal * move_b
    return True
