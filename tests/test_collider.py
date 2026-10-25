
import pytest

from pyphysics.physics2d.collider import CircleCollider


def test_circle_collider_creation():
    collider = CircleCollider(radius=0.5)
    assert collider.radius == 0.5


def test_circle_collider_invalid_radius():
    with pytest.raises(ValueError):
        CircleCollider(radius=0)

    with pytest.raises(ValueError):
        CircleCollider(radius=-1)
