"""Run after installation: python examples/free_fall_2d.py"""
from pyphysics.math import Vector2
from pyphysics.physics2d import Body2D, World2D

world = World2D(gravity=Vector2(0, -9.81))
ball = Body2D(position=Vector2(0, 10), velocity=Vector2(3, 0), mass=2)
world.add_body(ball)

print("time (s) | x (m) | y (m) | vy (m/s)")
for step in range(1, 61):
    world.step(1 / 60)
    if step % 10 == 0:
        print(f"{step / 60:8.3f} | {ball.position.x:5.2f} | {ball.position.y:5.2f} | {ball.velocity.y:8.2f}")
