
import pytest

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.collisions.position import correct_circle_positions


def make_ball(x, y, mass):
    return Body2D(
        position=Vector2(x, y),
        velocity=Vector2(0, 0),
        mass=mass,
    )


def test_equal_mass_correction():
    """Equal masses should move equal distances."""
    a = make_ball(0, 0, 1)
    b = make_ball(1.5, 0, 1)

    corrected = correct_circle_positions(a, 1, b, 1)

    assert corrected
    assert a.position.x == pytest.approx(-0.25)
    assert b.position.x == pytest.approx(1.75)


def test_different_mass_correction():
    """Lighter bodies should move farther."""
    a = make_ball(0, 0, 2)
    b = make_ball(1.2, 0, 6)

    corrected = correct_circle_positions(a, 1, b, 1)

    assert corrected
    assert a.position.x == pytest.approx(-0.6)
    assert b.position.x == pytest.approx(1.4)


def test_no_overlap():
    """Separated circles should not move."""
    a = make_ball(0, 0, 1)
    b = make_ball(5, 0, 1)

    corrected = correct_circle_positions(a, 1, b, 1)

    assert not corrected
    assert a.position == Vector2(0, 0)
    assert b.position == Vector2(5, 0)


def test_already_separating():
    """Overlapping circles must separate even if moving apart."""
    a = make_ball(0, 0, 1)
    b = make_ball(1.5, 0, 1)

    a.velocity = Vector2(-2, 0)
    b.velocity = Vector2(2, 0)

    assert correct_circle_positions(a, 1, b, 1)

    distance = (b.position - a.position).length()
    assert distance == pytest.approx(2.0)


def test_coincident_centers():
    """Coincident circles should still be separated."""
    a = make_ball(0, 0, 1)
    b = make_ball(0, 0, 1)

    assert correct_circle_positions(a, 1, b, 1)

    distance = (b.position - a.position).length()
    assert distance == pytest.approx(2.0)


def test_invalid_radius():
    a = make_ball(0, 0, 1)
    b = make_ball(1, 0, 1)

    with pytest.raises(ValueError):
        correct_circle_positions(a, 0, b, 1)

    with pytest.raises(ValueError):
        correct_circle_positions(a, 1, b, -1)
