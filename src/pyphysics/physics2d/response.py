
from dataclasses import dataclass

from .collision import calculate_toi


@dataclass(frozen=True)
class GroundStepResult:
    y: float
    vy: float
    impact_time: float | None


def step_ground(
    y: float,
    vy: float,
    gravity: float,
    dt: float,
    restitution: float = 1.0,
) -> GroundStepResult:
    """Advance vertical motion with a ground at y=0.

    Uses exact constant-acceleration motion and supports
    at most one ground impact per step.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if not 0 <= restitution <= 1:
        raise ValueError("Restitution must be between 0 and 1")
    if y < 0:
        raise ValueError("Object starts below ground")

    # Resting contact with a downward gravitational field.
    if y == 0 and vy <= 0 and gravity <= 0:
        return GroundStepResult(0.0, 0.0, None)

    toi = calculate_toi(y, vy, gravity, dt)

    if toi is None:
        new_y = y + vy * dt + 0.5 * gravity * dt**2
        new_vy = vy + gravity * dt

        return GroundStepResult(new_y, new_vy, None)

    # Velocity exactly at impact
    impact_vy = vy + gravity * toi

    # Reflect the velocity according to restitution
    rebound_vy = -restitution * impact_vy

    # Advance the remainder of this physics step
    remaining = dt - toi

    new_y = (
        rebound_vy * remaining
        + 0.5 * gravity * remaining**2
    )
    new_vy = rebound_vy + gravity * remaining

    # Basic resting-contact handling
    if new_y < 0:
        new_y = 0.0
        new_vy = 0.0

    return GroundStepResult(
        y=new_y,
        vy=new_vy,
        impact_time=toi,
    )

