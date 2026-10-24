# PyPhysics3D

A Python physics engine built from scratch, starting with 2D motion and evolving toward 3D rigid-body simulation.

## Current status (v0.1.0)

Implemented: immutable `Vector2`, 2D bodies, a world with uniform gravity, semi-implicit Euler integration, unit tests, and GitHub Actions.

Not implemented: collision detection, contacts, friction, rigid-body rotation, 3D simulation, or rendering.

## Installation

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Run

```bash
python examples/free_fall_2d.py
python -m pytest
```

## Conventions

- Right-handed Cartesian coordinates in 2D: +x right, +y up.
- SI units: meters, seconds, kilograms.
- Fixed timestep recommended: `dt = 1/60` seconds.

## Roadmap

- v0.1: 2D particle motion and tested integrator
- v0.2: circle collision and boundaries
- v0.3: rigid-body angular dynamics and impulse solver
- v0.4: interactive sandbox and renderer
- v0.5: start 3D math and physics modules
