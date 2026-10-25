
from pyphysics.math.vector2 import Vector2


def collision_normal(
    pos_a: Vector2,
    pos_b: Vector2,
) -> Vector2:
    """Return the unit normal pointing from A to B."""

    delta = pos_b - pos_a
    distance = delta.length()

    # Coincident centers: the normal is undefined.
    # Use a temporary fallback direction.
    if distance == 0:
        return Vector2(1, 0)

    return delta / distance
