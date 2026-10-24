"""Run after installation: python examples/free_fall_2d.py"""
from pyphysics.math import Vector2

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
dt = 1 / PHYSICS_HZ

print("Time (s) | Height (m) | Velocity (m/s)")

for step in range(1, PHYSICS_HZ + 1):
    world.step(dt)

    if step % 100 == 0:
        print(
            f"{step * dt:.3f} | "
            f"{ball.position.y:.6f} | "
            f"{ball.velocity.y:.6f}"
        )

