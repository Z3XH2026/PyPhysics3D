from dataclasses import dataclass


@dataclass(frozen=True)
class CircleCollider:
    radius: float

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError("Circle radius must be positive.")
