from dataclasses import dataclass, field
from pyphysics.math import Vector2
from .body import Body2D
from .response import step_ground


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
    def step_with_ground(
        self,
        dt: float,
        restitution: float = 1.0,
    ) -> list[float]:
        """Advance bodies with a horizontal ground at y=0.

        Returns impact times relative to this step.
        """
        impacts = []

        for body in self.bodies:
            result = step_ground(
                y=body.position.y,
                vy=body.velocity.y,
                gravity=self.gravity.y,
                dt=dt,
                restitution=restitution,
            )

            body.position = Vector2(
                body.position.x + body.velocity.x * dt,
                result.y,
            )

            body.velocity = Vector2(
                body.velocity.x,
                result.vy,
            )

            if result.impact_time is not None:
                impacts.append(result.impact_time)

        return impacts

