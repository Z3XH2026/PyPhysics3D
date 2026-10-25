import pytest

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.gravity.integrator import step_velocity_verlet


def test_zero_gravity():
    ball = Body2D(
        position=Vector2(0, 0),
        velocity=Vector2(3, 4),
        mass=2,
    )

    step_velocity_verlet(
        [ball],
        dt=2.0,
        gravitational_constant=0.0,
    )

    assert ball.position.x == pytest.approx(6)
    assert ball.position.y == pytest.approx(8)
    assert ball.velocity.x == pytest.approx(3)
    assert ball.velocity.y == pytest.approx(4)
def test_total_momentum_conservation():
    a = Body2D(
        position=Vector2(-2, 0),
        velocity=Vector2(0, 1),
        mass=2,
    )

    b = Body2D(
        position=Vector2(2, 0),
        velocity=Vector2(0, -1),
        mass=3,
    )

    initial_momentum = a.velocity * a.mass + b.velocity * b.mass

    for _ in range(100):
        step_velocity_verlet(
            [a, b],
            dt=0.01,
            gravitational_constant=1.0,
        )

    final_momentum = a.velocity * a.mass + b.velocity * b.mass

    assert final_momentum.x == pytest.approx(initial_momentum.x)
    assert final_momentum.y == pytest.approx(initial_momentum.y)

import math


def test_binary_orbit_stability():
    a = Body2D(
        position=Vector2(-1, 0),
        velocity=Vector2(0, 0.5),
        mass=1,
    )

    b = Body2D(
        position=Vector2(1, 0),
        velocity=Vector2(0, -0.5),
        mass=1,
    )

    initial_distance = (b.position - a.position).length()

    # Angular velocity: omega = v / R = 0.5 rad/s
    # Orbital period: T = 2*pi / omega = 4*pi seconds
    period = 4 * math.pi

    dt = 0.001
    steps = round(period / dt)

    for _ in range(steps):
        step_velocity_verlet(
            [a, b],
            dt=dt,
            gravitational_constant=1.0,
        )

    final_distance = (b.position - a.position).length()

    # Separation should remain close to 2 m
    assert final_distance == pytest.approx(
        initial_distance, abs=0.01
    )

    # After one revolution, both bodies should return
    # close to their initial positions.
    assert a.position.x == pytest.approx(-1, abs=0.01)
    assert a.position.y == pytest.approx(0, abs=0.01)

    assert b.position.x == pytest.approx(1, abs=0.01)
    assert b.position.y == pytest.approx(0, abs=0.01)
