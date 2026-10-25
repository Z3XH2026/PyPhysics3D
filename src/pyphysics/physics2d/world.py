from dataclasses import dataclass, field
from pyphysics.math import Vector2
from .body import Body2D
from .response import step_ground
from pyphysics.physics2d.collider import CircleCollider
from pyphysics.physics2d.circle_response import resolve_circle_collision
from .collisions.position import correct_circle_positions


@dataclass
class World2D:
    gravity: Vector2 = field(default_factory=lambda: Vector2(0.0, -9.81))
    bodies: list[Body2D] = field(default_factory=list)
    colliders: list[CircleCollider | None] = field(default_factory=list)

    def add_body(self, body: Body2D, collider: CircleCollider | None = None, ) -> None:
        self.bodies.append(body)
        self.colliders.append(collider)

  
    def step(self, dt: float) -> None:
        """Semi-implicit Euler integration and circle collision response."""
        if dt <= 0:
            raise ValueError("dt must be positive")

        # 1. Update velocities and positions
        for body in self.bodies:
            body.velocity = body.velocity + self.gravity * dt
            body.position = body.position + body.velocity * dt

        # 2. Detect and resolve circle collisions
        for i in range(len(self.bodies)):
            collider_a = self.colliders[i]

            if collider_a is None:
                continue

            for j in range(i + 1, len(self.bodies)):
                collider_b = self.colliders[j]

                if collider_b is None:
                    continue

                resolve_circle_collision(
                    self.bodies[i],
                    collider_a.radius,
                    self.bodies[j],
                    collider_b.radius,
                )
                correct_circle_positions(
                    self.bodies[i],
                    collider_a.radius,
                    self.bodies[j],
                    collider_b.radius,
                )

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

