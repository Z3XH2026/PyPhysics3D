from dataclasses import dataclass

from .toi import calculate_toi


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
    """Advance a point-like body above horizontal ground y=0.

    Uses analytic constant-acceleration motion, with up to one ground impact
    per step. The radius of a rendered ball is not modeled here.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if not 0 <= restitution <= 1:
        raise ValueError("Restitution must be between 0 and 1")

    # Contact at rest: prevent gravity from dragging the body below ground.
    if y <= 0 and vy <= 0 and gravity <= 0 and abs(vy) < 1e-12:
        return GroundStepResult(y=0.0, vy=0.0, impact_time=None)

    toi = calculate_toi(y, vy, gravity, dt)
    if toi is None:
        new_y = y + vy * dt + 0.5 * gravity * dt * dt
        new_vy = vy + gravity * dt
        return GroundStepResult(y=new_y, vy=new_vy, impact_time=None)

    impact_vy = vy + gravity * toi
    rebound_vy = -restitution * impact_vy
    remaining = dt - toi
    new_y = rebound_vy * remaining + 0.5 * gravity * remaining**2
    new_vy = rebound_vy + gravity * remaining
    # A zero-restitution impact should remain on the ground rather than sink.
    if new_y < 0:
        new_y = 0.0
        new_vy = 0.0
    return GroundStepResult(y=new_y, vy=new_vy, impact_time=toi)
