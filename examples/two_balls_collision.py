
import pygame

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.collider import CircleCollider
from pyphysics.physics2d.world import World2D


# Window settings
WIDTH, HEIGHT = 900, 500
FPS = 60
PHYSICS_DT = 1 / 600
PIXELS_PER_METER = 50

# Ball settings
RADIUS = 0.5
BALL_RADIUS_PX = int(RADIUS * PIXELS_PER_METER)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyPhysics3D - Two Ball Collision")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)


def create_world():
    world = World2D(gravity=Vector2(0, 0))

    ball_a = Body2D(
        position=Vector2(-3, 0),
        velocity=Vector2(5, 0),
        mass=1,
    )

    ball_b = Body2D(
        position=Vector2(3, 0),
        velocity=Vector2(0, 0),
        mass=1,
    )

    world.add_body(ball_a, CircleCollider(RADIUS))
    world.add_body(ball_b, CircleCollider(RADIUS))

    return world, ball_a, ball_b


def to_screen(position):
    return (
        int(WIDTH / 2 + position.x * PIXELS_PER_METER),
        int(HEIGHT / 2 - position.y * PIXELS_PER_METER),
    )


world, ball_a, ball_b = create_world()

running = True
paused = False
accumulator = 0.0

while running:
    frame_dt = min(clock.tick(FPS) / 1000, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key == pygame.K_r:
                world, ball_a, ball_b = create_world()
                accumulator = 0.0

    if not paused:
        accumulator += frame_dt

        while accumulator >= PHYSICS_DT:
            world.step(PHYSICS_DT)
            accumulator -= PHYSICS_DT

    screen.fill((18, 25, 40))

    # Draw horizontal axis
    pygame.draw.line(
        screen,
        (85, 95, 115),
        (0, HEIGHT // 2),
        (WIDTH, HEIGHT // 2),
        1,
    )

    # Draw balls using the engine's positions
    pygame.draw.circle(
        screen,
        (80, 170, 255),
        to_screen(ball_a.position),
        BALL_RADIUS_PX,
    )

    pygame.draw.circle(
        screen,
        (255, 170, 75),
        to_screen(ball_b.position),
        BALL_RADIUS_PX,
    )

    # Total momentum and kinetic energy
    momentum = (
        ball_a.velocity * ball_a.mass
        + ball_b.velocity * ball_b.mass
    )

    energy = (
        0.5 * ball_a.mass * ball_a.velocity.dot(ball_a.velocity)
        + 0.5 * ball_b.mass * ball_b.velocity.dot(ball_b.velocity)
    )

    lines = [
        f"Ball A vx: {ball_a.velocity.x:.2f} m/s",
        f"Ball B vx: {ball_b.velocity.x:.2f} m/s",
        f"Total momentum X: {momentum.x:.2f} kg m/s",
        f"Total kinetic energy: {energy:.2f} J",
        "SPACE: Pause | R: Reset",
    ]

    for i, line in enumerate(lines):
        label = font.render(line, True, (230, 235, 245))
        screen.blit(label, (20, 20 + i * 29))

    pygame.display.flip()

pygame.quit()
