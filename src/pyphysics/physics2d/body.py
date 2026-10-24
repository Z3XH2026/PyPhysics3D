from dataclasses import dataclass, field
from pyphysics.math import Vector2


@dataclass
class Body2D:
    position: Vector2
    velocity: Vector2 = field(default_factory=lambda: Vector2(0.0, 0.0))
    mass: float = 1.0

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise ValueError("Mass must be greater than zero")
