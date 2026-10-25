from pyphysics.math.vector2 import Vector2
def circles_overlap(
    pos_a: Vector2,
    radius_a: float,
    pos_b: Vector2,
    radius_b: float,
) -> bool:
    delta = pos_b - pos_a
    radius_sum = radius_a + radius_b

    return delta.dot(delta) <= radius_sum ** 2