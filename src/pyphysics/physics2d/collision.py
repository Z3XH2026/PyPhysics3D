
from math import sqrt


def calculate_toi(y0, v0, g, dt):
    """Calculate when a particle hits the ground."""

    if y0 < 0 or dt <= 0:
        raise ValueError("Invalid initial height or dt")

    if abs(g) < 1e-12:
        if v0 >= 0:
            return None
        t = -y0 / v0
        return t if 0 <= t <= dt else None

    discriminant = v0**2 - 2 * g * y0

    if discriminant < 0:
        return None

    root = sqrt(discriminant)

    t1 = (-v0 + root) / g
    t2 = (-v0 - root) / g

    # Keep collision times within this physics step
    valid = [
    t for t in (t1, t2)
    if 0 <= t <= dt
    and v0 + g * t < 0
]
    return min(valid) if valid else None
