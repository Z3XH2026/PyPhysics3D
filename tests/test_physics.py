import pytest
from pyphysics.math import Vector2
from pyphysics.physics2d import Body2D, World2D


def test_vector_addition():
    assert Vector2(1, 2) + Vector2(3, 4) == Vector2(4, 6)


def test_vector_length():
    assert Vector2(3, 4).length() == pytest.approx(5)


def test_one_step_semi_implicit_euler():
    world = World2D(gravity=Vector2(0, -10))
    ball = Body2D(position=Vector2(0, 10), velocity=Vector2(3, 0), mass=2)
    world.add_body(ball)
    world.step(0.1)
    assert ball.velocity == Vector2(3, -1)
    assert ball.position.x == pytest.approx(0.3)
    assert ball.position.y == pytest.approx(9.9)


def test_mass_must_be_positive():
    with pytest.raises(ValueError):
        Body2D(position=Vector2(0, 0), mass=0)
