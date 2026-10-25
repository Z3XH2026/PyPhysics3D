from pyphysics.physics2d.body import Body2D
from .newtonian import G
from .nbody import nbody_accelerations


def step_velocity_verlet(
    bodies: list[Body2D],
    dt: float,
    gravitational_constant: float = G,
) -> None:
    if dt <= 0:
        raise ValueError("dt must be positive")

    # 1. Calculate accelerations at old positions
    old_accelerations = nbody_accelerations(
        bodies, gravitational_constant
    )

    # 2. Update all positions
    for body, acceleration in zip(bodies, old_accelerations):
        body.position = (
            body.position
            + body.velocity * dt
            + acceleration * (0.5 * dt**2)
        )

    # 3. Calculate accelerations at new positions
    new_accelerations = nbody_accelerations(
        bodies, gravitational_constant
    )

    # 4. Update velocities
    for body, old_acceleration, new_acceleration in zip(
        bodies, old_accelerations, new_accelerations
    ):
        body.velocity = (
            body.velocity
            + 0.5 * (old_acceleration + new_acceleration) * dt
        )