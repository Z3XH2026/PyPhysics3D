
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.circle import circles_overlap
from pyphysics.physics2d.contact import collision_normal


def resolve_circle_collision(
    body_a: Body2D,
    radius_a: float,
    body_b: Body2D,
    radius_b: float,
    restitution: float = 1.0,
) -> bool:
    """Resolve the velocity response of two overlapping circles."""

    if not 0.0 <= restitution <= 1.0:
        raise ValueError("Restitution must be between 0 and 1.")

    if radius_a <= 0 or radius_b <= 0:
        raise ValueError("Circle radii must be positive.")

    # 1. Detect collision
    if not circles_overlap(
        body_a.position, radius_a,
        body_b.position, radius_b,
    ):
        return False

    # 2. Calculate collision normal
    normal = collision_normal(
        body_a.position,
        body_b.position,
    )

    # 3. Calculate relative velocity
    relative_velocity = body_b.velocity - body_a.velocity
    velocity_along_normal = relative_velocity.dot(normal)

    # Objects are already separating
    if velocity_along_normal >= 0:
        return False

    # 4. Calculate collision impulse
    inverse_mass_a = 1.0 / body_a.mass
    inverse_mass_b = 1.0 / body_b.mass

    impulse_magnitude = (
        -(1.0 + restitution) * velocity_along_normal
        / (inverse_mass_a + inverse_mass_b)
    )

    impulse = normal * impulse_magnitude

    # 5. Apply impulse
    body_a.velocity = body_a.velocity - impulse * inverse_mass_a
    body_b.velocity = body_b.velocity + impulse * inverse_mass_b

    return True
