"""Unit tests for direct N-body gravity summation."""

import pytest

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.gravity.nbody import nbody_accelerations
from pyphysics.physics2d.gravity.newtonian import gravitational_accelerations


def body(x: float, y: float, mass: float) -> Body2D:
    return Body2D(
        position=Vector2(x, y), velocity=Vector2(0, 0), mass=mass
    )


def test_empty_system():
    assert nbody_accelerations([]) == []


def test_single_body_has_no_mutual_gravity():
    assert nbody_accelerations([body(10, 20, 5)]) == [Vector2(0, 0)]


def test_two_body_matches_pairwise_calculation():
    a = body(0, 0, 2)
    b = body(3, 0, 6)
    expected_a, expected_b = gravitational_accelerations(a, b, 1.0)
    actual = nbody_accelerations([a, b], 1.0)
    assert actual[0].x == pytest.approx(expected_a.x)
    assert actual[0].y == pytest.approx(expected_a.y)
    assert actual[1].x == pytest.approx(expected_b.x)
    assert actual[1].y == pytest.approx(expected_b.y)


def test_three_body_superposition():
    # A is pulled right by B and up by C.
    a = body(0, 0, 1)
    b = body(2, 0, 4)
    c = body(0, 3, 9)
    accelerations = nbody_accelerations([a, b, c], 1.0)
    assert accelerations[0].x == pytest.approx(1.0)
    assert accelerations[0].y == pytest.approx(1.0)


def test_total_internal_force_is_zero():
    bodies = [body(0, 0, 1), body(2, 0, 2), body(0, 3, 3)]
    accelerations = nbody_accelerations(bodies, 1.0)
    total_force = Vector2(0, 0)
    for current, acceleration in zip(bodies, accelerations):
        total_force = total_force + acceleration * current.mass
    assert total_force.x == pytest.approx(0, abs=1e-12)
    assert total_force.y == pytest.approx(0, abs=1e-12)


def test_does_not_mutate_bodies():
    bodies = [body(0, 0, 1), body(2, 0, 2)]
    previous = [(b.position, b.velocity) for b in bodies]
    nbody_accelerations(bodies, 1.0)
    assert [(b.position, b.velocity) for b in bodies] == previous


def test_coincident_bodies_raise():
    with pytest.raises(ValueError):
        nbody_accelerations([body(0, 0, 1), body(0, 0, 2)], 1.0)


@pytest.mark.parametrize("g", [-1, float("nan"), float("inf")])
def test_invalid_constant(g):
    with pytest.raises(ValueError):
        nbody_accelerations([], g)
