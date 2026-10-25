import pytest

from pyphysics.math.vector2 import Vector2
from pyphysics.physics2d.contact import collision_normal


def test_collision_normal():
    normal = collision_normal(
        Vector2(1, 2),
        Vector2(4, 6),
    )

    assert normal.x == pytest.approx(0.6)
    assert normal.y == pytest.approx(0.8)