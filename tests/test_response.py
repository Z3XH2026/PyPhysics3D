
import pytest

from pyphysics.physics2d.response import step_ground


def test_no_collision():
    result = step_ground(
        y=10, vy=0, gravity=-10, dt=0.1
    )

    assert result.impact_time is None
    assert result.y == pytest.approx(9.95)
    assert result.vy == pytest.approx(-1.0)


def test_elastic_collision():
    result = step_ground(
        y=10, vy=-5, gravity=-10,
        dt=1.2, restitution=1.0
    )

    assert result.impact_time == pytest.approx(1.0)
    assert result.y == pytest.approx(2.8)
    assert result.vy == pytest.approx(13.0)


def test_inelastic_collision():
    result = step_ground(
        y=10, vy=-5, gravity=-10,
        dt=1.2, restitution=0.8
    )

    assert result.impact_time == pytest.approx(1.0)
    assert result.y == pytest.approx(2.2)
    assert result.vy == pytest.approx(10.0)


def test_ball_leaving_ground():
    result = step_ground(
        y=0, vy=10, gravity=-9.81, dt=0.01
    )

    assert result.impact_time is None
    assert result.y > 0


def test_resting_on_ground():
    result = step_ground(
        y=0, vy=0, gravity=-9.81, dt=0.01
    )

    assert result.y == 0
    assert result.vy == 0


def test_invalid_restitution():
    with pytest.raises(ValueError):
        step_ground(
            y=10, vy=0, gravity=-9.81,
            dt=0.1, restitution=1.5
        )


def test_energy_conservation():
    mass = 2.0
    g = 9.81

    result = step_ground(
        y=10, vy=0, gravity=-g,
        dt=2.0, restitution=1.0
    )

    initial_energy = mass * g * 10

    final_energy = (
        0.5 * mass * result.vy**2
        + mass * g * result.y
    )

    assert final_energy == pytest.approx(
        initial_energy, abs=1e-9
    )