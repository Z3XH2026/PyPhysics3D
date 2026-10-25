
import pytest

from pyphysics.math.vector2 import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.circle_response import resolve_circle_collision


def make_ball(x, y, vx, vy, mass):
    return Body2D(
        position=Vector2(x, y),
        velocity=Vector2(vx, vy),
        mass=mass,
    )


def kinetic_energy(body):
    return 0.5 * body.mass * body.velocity.dot(body.velocity)


def test_equal_mass_elastic_collision():
    a = make_ball(0, 0, 3, 0, 2)
    b = make_ball(2, 0, 0, 0, 2)

    assert resolve_circle_collision(a, 1, b, 1, restitution=1.0)

    assert a.velocity.x == pytest.approx(0)
    assert b.velocity.x == pytest.approx(3)


def test_different_mass_elastic_collision():
    a = make_ball(0, 0, 3, 0, 1)
    b = make_ball(2, 0, 0, 0, 2)

    assert resolve_circle_collision(a, 1, b, 1, restitution=1.0)

    assert a.velocity.x == pytest.approx(-1)
    assert b.velocity.x == pytest.approx(2)


def test_perfectly_inelastic_collision():
    a = make_ball(0, 0, 3, 0, 2)
    b = make_ball(2, 0, 0, 0, 2)

    assert resolve_circle_collision(a, 1, b, 1, restitution=0.0)

    assert a.velocity.x == pytest.approx(1.5)
    assert b.velocity.x == pytest.approx(1.5)


def test_oblique_collision():
    a = make_ball(0, 0, 3, 4, 1)
    b = make_ball(0, 2, 0, 0, 1)

    assert resolve_circle_collision(a, 1, b, 1, restitution=1.0)

    assert a.velocity.x == pytest.approx(3)
    assert a.velocity.y == pytest.approx(0)
    assert b.velocity.x == pytest.approx(0)
    assert b.velocity.y == pytest.approx(4)


def test_momentum_and_energy_conservation():
    a = make_ball(0, 0, 3, 4, 2)
    b = make_ball(2, 0, -1, 2, 3)

    initial_momentum = a.velocity * a.mass + b.velocity * b.mass
    initial_energy = kinetic_energy(a) + kinetic_energy(b)

    assert resolve_circle_collision(a, 1, b, 1, restitution=1.0)

    final_momentum = a.velocity * a.mass + b.velocity * b.mass
    final_energy = kinetic_energy(a) + kinetic_energy(b)

    assert final_momentum.x == pytest.approx(initial_momentum.x)
    assert final_momentum.y == pytest.approx(initial_momentum.y)
    assert final_energy == pytest.approx(initial_energy)


def test_no_collision():
    a = make_ball(0, 0, 3, 0, 1)
    b = make_ball(5, 0, 0, 0, 1)

    assert not resolve_circle_collision(a, 1, b, 1)
    assert a.velocity == Vector2(3, 0)
    assert b.velocity == Vector2(0, 0)


def test_already_separating():
    a = make_ball(0, 0, -1, 0, 1)
    b = make_ball(2, 0, 1, 0, 1)

    assert not resolve_circle_collision(a, 1, b, 1)
    assert a.velocity.x == -1
    assert b.velocity.x == 1


def test_invalid_restitution():
    a = make_ball(0, 0, 3, 0, 1)
    b = make_ball(2, 0, 0, 0, 1)

    with pytest.raises(ValueError):
        resolve_circle_collision(a, 1, b, 1, restitution=1.5)
