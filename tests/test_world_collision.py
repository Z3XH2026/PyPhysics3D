
import pytest

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.collider import CircleCollider
from pyphysics.physics2d.world import World2D


def test_automatic_circle_collision():
    world = World2D(gravity=Vector2(0, 0))

    ball_a = Body2D(
        position=Vector2(0, 0),
        velocity=Vector2(3, 0),
        mass=1,
    )

    ball_b = Body2D(
        position=Vector2(2, 0),
        velocity=Vector2(0, 0),
        mass=1,
    )

    world.add_body(ball_a, CircleCollider(radius=1))
    world.add_body(ball_b, CircleCollider(radius=1))

    world.step(0.01)

    assert ball_a.velocity.x == pytest.approx(0)
    assert ball_b.velocity.x == pytest.approx(3)

def test_world_corrects_circle_overlap():
    world = World2D(gravity=Vector2(0, 0))

    ball_a = Body2D(
        position=Vector2(0, 0),
        velocity=Vector2(0, 0),
        mass=1,
    )

    ball_b = Body2D(
        position=Vector2(1.5, 0),
        velocity=Vector2(0, 0),
        mass=1,
    )

    world.add_body(ball_a, CircleCollider(radius=1))
    world.add_body(ball_b, CircleCollider(radius=1))

    world.step(0.01)

    distance = (ball_b.position - ball_a.position).length()

    assert distance == pytest.approx(2.0)
    assert ball_a.position.x == pytest.approx(-0.25)
    assert ball_b.position.x == pytest.approx(1.75)