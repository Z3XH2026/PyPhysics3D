"""Unit tests for Newtonian two-body gravitational accelerations."""

import pytest

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.gravity.newtonian import gravitational_accelerations


def body(x: float, y: float, mass: float) -> Body2D:
    return Body2D(
        position=Vector2(x, y), velocity=Vector2(0, 0), mass=mass
    )


def test_gravitational_accelerations():
    a = body(0, 0, 2)
    b = body(3, 0, 6)

    accel_a, accel_b = gravitational_accelerations(
        a, b, gravitational_constant=1.0
    )

    assert accel_a.x == pytest.approx(2 / 3)
    assert accel_a.y == pytest.approx(0)
    assert accel_b.x == pytest.approx(-2 / 9)
    assert accel_b.y == pytest.approx(0)


def test_force_balance():
    a = body(0, 0, 2)
    b = body(3, 4, 6)
    accel_a, accel_b = gravitational_accelerations(a, b, 1.0)

    force_sum = accel_a * a.mass + accel_b * b.mass
    assert force_sum.x == pytest.approx(0)
    assert force_sum.y == pytest.approx(0)


def test_inverse_square_distance():
    a = body(0, 0, 1)
    near = body(1, 0, 6)
    far = body(3, 0, 6)
    accel_near, _ = gravitational_accelerations(a, near, 1.0)
    accel_far, _ = gravitational_accelerations(a, far, 1.0)
    assert accel_far.x == pytest.approx(accel_near.x / 9)


def test_coincident_positions_raise():
    a = body(0, 0, 1)
    b = body(0, 0, 2)
    with pytest.raises(ValueError):
        gravitational_accelerations(a, b)


@pytest.mark.parametrize("g", [-1, float("nan"), float("inf")])
def test_invalid_constant(g):
    with pytest.raises(ValueError):
        gravitational_accelerations(body(0, 0, 1), body(1, 0, 1), g)
