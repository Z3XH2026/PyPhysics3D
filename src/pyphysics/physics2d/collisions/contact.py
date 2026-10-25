from pyphysics.math.vector2 import Vector2


def collision_normal(pos_a: Vector2, pos_b: Vector2) -> Vector2:
    """Unit vector from center A to center B.

    If centers coincide, use a fixed fallback direction.
    """
    delta = pos_b - pos_a
    distance = delta.length()
    if distance == 0:
        return Vector2(1, 0)
    return delta / distance
