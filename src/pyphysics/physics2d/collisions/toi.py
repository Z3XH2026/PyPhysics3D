from math import sqrt


def calculate_toi(y0: float, v0: float, g: float, dt: float) -> float | None:
    """First descending crossing of ground y=0 during [0, dt].

    Motion follows y(t) = y0 + v0*t + 0.5*g*t**2.
    Return None when there is no descending ground crossing.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")

    eps = 1e-12
    if abs(g) < eps:
        if v0 >= 0:
            return None
        t = -y0 / v0
        return t if 0 <= t <= dt else None

    discriminant = v0 * v0 - 2.0 * g * y0
    if discriminant < 0:
        return None
    root = sqrt(discriminant)
    times = [(-v0 - root) / g, (-v0 + root) / g]
    candidates = [t for t in times if 0 <= t <= dt and v0 + g * t < 0]
    return min(candidates) if candidates else None
