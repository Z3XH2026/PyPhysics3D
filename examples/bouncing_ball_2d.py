
from pyphysics.math import Vector2
from pyphysics.physics2d import Body2D, World2D

world = World2D(gravity=Vector2(0, -9.81))

ball = Body2D(
    position=Vector2(0, 10),
    velocity=Vector2(3, 0),
    mass=2
)

world.add_body(ball)

PHYSICS_HZ = 600
DT = 1 / PHYSICS_HZ
DURATION = 10
RESTITUTION = 1.0

print("Time (s) | Height (m) | Energy (J)")

for step in range(1, PHYSICS_HZ * DURATION + 1):

    impacts = world.step_with_ground(
        DT,
        restitution=RESTITUTION
    )

    for impact in impacts:
        collision_time = (step - 1) * DT + impact
        print(f"Bounce at {collision_time:.6f} s")

    # Kinetic energy
    kinetic = 0.5 * ball.mass * (
        ball.velocity.x**2 + ball.velocity.y**2
    )

    # Gravitational potential energy
    potential = ball.mass * 9.81 * ball.position.y

    total_energy = kinetic + potential

    if step % PHYSICS_HZ == 0:
        print(
            f"{step * DT:.1f} | "
            f"{ball.position.y:.6f} | "
            f"{total_energy:.6f}"
        )
