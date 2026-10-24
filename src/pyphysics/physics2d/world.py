from dataclasses import dataclass, field
from pyphysics.math import Vector2
from .body import Body2D


@dataclass
class World2D:
    gravity: Vector2 = field(default_factory=lambda: Vector2(0.0, -9.81))
    bodies: list[Body2D] = field(default_factory=list)

    def add_body(self, body: Body2D) -> None:
        self.bodies.append(body)

    def step(self, dt: float) -> None:
        """Semi-implicit Euler integration with constant gravity."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        for body in self.bodies:
            body.velocity = body.velocity + self.gravity * dt
            body.position = body.position + body.velocity * dt
