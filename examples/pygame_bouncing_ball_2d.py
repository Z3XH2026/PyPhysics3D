
import pygame

from pyphysics.math import Vector2
from pyphysics.physics2d import Body2D, World2D

# Window settings
WIDTH, HEIGHT = 900, 600
RENDER_FPS = 60
PHYSICS_HZ = 600
PHYSICS_DT = 1 / PHYSICS_HZ

# Physics settings
PIXELS_PER_METER = 35
GROUND_Y = HEIGHT - 60
RESTITUTION = 0.8

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyPhysics3D - 2D Sandbox")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)

world = World2D(gravity=Vector2(0, -9.81))
ball = Body2D(
    position=Vector2(0, 10),
    velocity=Vector2(0, 0),
    mass=2
)
world.add_body(ball)

running = True
paused = False
accumulator = 0.0
simulation_time = 0.0

while running:
    frame_dt = min(clock.tick(RENDER_FPS) / 1000, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    if not paused:
        accumulator += frame_dt

        while accumulator >= PHYSICS_DT:
            world.step_with_ground(
                PHYSICS_DT,
                restitution=RESTITUTION
            )
            accumulator -= PHYSICS_DT
            simulation_time += PHYSICS_DT

    # Convert physical coordinates to screen coordinates
    screen_x = WIDTH // 2 + ball.position.x * PIXELS_PER_METER
    BALL_RADIUS = 12
    screen_y = (
        GROUND_Y
        - ball.position.y * PIXELS_PER_METER
        - BALL_RADIUS
    )

    screen.fill((18, 25, 40))

    pygame.draw.line(
        screen, (130, 150, 175),
        (0, GROUND_Y), (WIDTH, GROUND_Y), 3
    )

    pygame.draw.circle(
        screen, (80, 170, 255),
        (int(screen_x), int(screen_y)), 12
    )

    kinetic = 0.5 * ball.mass * (
        ball.velocity.x**2 + ball.velocity.y**2
    )
    potential = ball.mass * 9.81 * ball.position.y
    energy = kinetic + potential

    info = [
        f"Simulation time: {simulation_time:.2f} s",
        f"Height: {ball.position.y:.3f} m",
        f"Vertical velocity: {ball.velocity.y:.3f} m/s",
        f"Mechanical energy: {energy:.3f} J",
        "SPACE: Pause / Resume",
    ]

    for i, line in enumerate(info):
        image = font.render(line, True, (230, 235, 245))
        screen.blit(image, (20, 20 + 30 * i))

    pygame.display.flip()

pygame.quit()
