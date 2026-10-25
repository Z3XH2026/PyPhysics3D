
from pyphysics.math.vector2 import Vector2
from pyphysics.physics2d.circle import circles_overlap


def test_circles_separated():
    assert not circles_overlap(
        Vector2(0, 0), 1,
        Vector2(5, 0), 1,
    )


def test_circles_touching():
    assert circles_overlap(
        Vector2(0, 0), 1,
        Vector2(2, 0), 1,
    )


def test_circles_overlapping():
    assert circles_overlap(
        Vector2(0, 0), 2,
        Vector2(3, 0), 2,
    )


def test_circles_different_radii():
    assert circles_overlap(
        Vector2(1, 2), 2,
        Vector2(4, 6), 4,
    )
