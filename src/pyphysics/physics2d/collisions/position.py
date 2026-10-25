from ..body import Body2D
from .contact import collision_normal


def correct_circle_positions(
    body_a: Body2D,
    radius_a: float,
    body_b: Body2D,
    radius_b: float,
) -> bool:
    """Separate overlapping circles, weighted by inverse mass.

    Return True only if positions were corrected.
    """
    if radius_a <= 0 or radius_b <= 0:
        raise ValueError("Circle radii must be positive")

    delta = body_b.position - body_a.position
    distance = delta.length()
    penetration = radius_a + radius_b - distance
    if penetration <= 0:
        return False

    normal = collision_normal(body_a.position, body_b.position)
    inverse_mass_a = 1.0 / body_a.mass
    inverse_mass_b = 1.0 / body_b.mass
    inverse_mass_sum = inverse_mass_a + inverse_mass_b

    move_a = penetration * inverse_mass_a / inverse_mass_sum
    move_b = penetration * inverse_mass_b / inverse_mass_sum
    body_a.position = body_a.position - normal * move_a
    body_b.position = body_b.position + normal * move_b
    return True
