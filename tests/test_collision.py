import pytest

from pyphysics.physics2d.collision import calculate_toi


def test_free_fall_collision():
    # Start 10 m above ground, initially at rest
    t = calculate_toi(
        y0=10,
        v0=0,
        g=-10,
        dt=2
    )

    assert t == pytest.approx(2**0.5)


def test_collision_with_initial_velocity():
    # Start at 10 m, moving downward at 5 m/s
    t = calculate_toi(
        y0=10,
        v0=-5,
        g=-10,
        dt=2
    )

    assert t == pytest.approx(1.0)


def test_no_collision_within_step():
    # Impact happens after the current time step
    t = calculate_toi(
        y0=10,
        v0=0,
        g=-10,
        dt=0.1
    )

    assert t is None


def test_constant_velocity_collision():
    # No gravity, moving downward at 5 m/s
    t = calculate_toi(
        y0=10,
        v0=-5,
        g=0,
        dt=3
    )

    assert t == pytest.approx(2.0)
def test_ball_leaving_ground():
    t = calculate_toi(
        y0=0,
        v0=10,
        g=-9.81,
        dt=0.01
    )

    assert t is None
