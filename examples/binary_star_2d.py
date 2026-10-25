

"""Interactive N-body demo for PyPhysics3D (Pygame only).

Run from the repository root after installing PyPhysics3D and pygame:
    python examples/binary_star_2d.py

The control panel edits INITIAL conditions; Apply restarts the simulation.
"""

import math
import pygame

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.gravity.integrator import step_velocity_verlet

WINDOW_W, WINDOW_H = 1160, 720
PANEL_W = 325
VIEW_W = WINDOW_W - PANEL_W
FPS = 60
PHYSICS_DT = 0.002
MAX_PHYSICS_STEPS_PER_FRAME = 500
TRAIL_EVERY = 5
MAX_TRAIL_POINTS = 4000
ZOOM_FACTOR = 1.15
MIN_SCALE, MAX_SCALE = 4.0, 1000.0

BG = (13, 18, 32)
PANEL_BG = (25, 32, 48)
INPUT_BG = (38, 48, 68)
BORDER = (89, 105, 128)
TEXT = (232, 237, 246)
MUTED = (167, 179, 197)
ACCENT = (75, 157, 247)
ORANGE = (255, 175, 80)
GREEN = (65, 192, 145)
RED = (244, 109, 113)

DEFAULTS = {
    "G": 1.0,
    "A mass": 1.0,
    "A x": -1.0,
    "A y": 0.0,
    "A vx": 0.0,
    "A vy": 0.5,
    "B mass": 1.0,
    "B x": 1.0,
    "B y": 0.0,
    "B vx": 0.0,
    "B vy": -0.5,
}

pygame.init()
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("PyPhysics3D | N-body Lab")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)
small_font = pygame.font.SysFont("consolas", 15)
title_font = pygame.font.SysFont("consolas", 24, bold=True)


class NumberInput:
    def __init__(self, label, rect, value):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.text = format(value, ".8g")
        self.active = False
        self.error = False

    def set_value(self, value):
        self.text = format(value, ".8g")
        self.error = False

    def draw(self):
        label_img = small_font.render(self.label, True, MUTED)
        screen.blit(label_img, (self.rect.x, self.rect.y - 17))
        color = RED if self.error else ACCENT if self.active else BORDER
        pygame.draw.rect(screen, INPUT_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, color, self.rect, 2 if self.active else 1, border_radius=5)
        displayed = self.text[-15:]
        rendered = font.render(displayed + ("|" if self.active and pygame.time.get_ticks() // 500 % 2 == 0 else ""), True, TEXT)
        screen.blit(rendered, (self.rect.x + 8, self.rect.y + 7))

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.error = False
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                self.active = False
            elif len(self.text) < 22 and event.unicode in "0123456789+-.eE":
                self.text += event.unicode
                self.error = False

    def parse(self):
        try:
            value = float(self.text)
            if not math.isfinite(value):
                raise ValueError
            self.error = False
            return value
        except ValueError:
            self.error = True
            raise ValueError(f"Invalid number in {self.label}") from None


fields = {}
start_y = 106
for row, (label, value) in enumerate(DEFAULTS.items()):
    x = VIEW_W + 20 + (row % 2) * 153
    y = start_y + (row // 2) * 66
    fields[label] = NumberInput(label, (x, y, 137, 31), value)

apply_btn = pygame.Rect(VIEW_W + 20, 526, 137, 39)
reset_btn = pygame.Rect(VIEW_W + 173, 526, 132, 39)


def make_bodies(params):
    a = Body2D(
        position=Vector2(params["A x"], params["A y"]),
        velocity=Vector2(params["A vx"], params["A vy"]),
        mass=params["A mass"],
    )
    b = Body2D(
        position=Vector2(params["B x"], params["B y"]),
        velocity=Vector2(params["B vx"], params["B vy"]),
        mass=params["B mass"],
    )
    return [a, b]


def check_params(params):
    if params["G"] < 0:
        raise ValueError("G must be >= 0")
    for label in ("A mass", "B mass"):
        if params[label] <= 0:
            raise ValueError(f"{label} must be > 0")
    if (params["A x"] == params["B x"] and
            params["A y"] == params["B y"] and params["G"] > 0):
        raise ValueError("Bodies cannot start at the same position")


params = dict(DEFAULTS)
bodies = make_bodies(params)
trails = [[body.position] for body in bodies]
scale = 145.0
camera = Vector2(0, 0)
paused = False
sim_time = 0.0
accumulator = 0.0
steps_count = 0
message = "Edit parameters, then click Apply"
message_color = MUTED


def to_screen(position):
    return (int(VIEW_W / 2 + (position.x - camera.x) * scale),
            int(WINDOW_H / 2 - (position.y - camera.y) * scale))


def to_world(point):
    return Vector2(camera.x + (point[0] - VIEW_W / 2) / scale,
                   camera.y - (point[1] - WINDOW_H / 2) / scale)


def center_of_mass():
    total = sum(b.mass for b in bodies)
    numerator = Vector2(0.0, 0.0)
    for b in bodies:
        numerator = numerator + b.position * b.mass
    return numerator / total


def start_simulation(new_params):
    global params, bodies, trails, sim_time, accumulator, steps_count, paused
    check_params(new_params)
    params = new_params
    bodies = make_bodies(params)
    trails = [[body.position] for body in bodies]
    sim_time = 0.0
    accumulator = 0.0
    steps_count = 0
    paused = False


def draw_button(rect, label, color):
    pygame.draw.rect(screen, color, rect, border_radius=6)
    rendered = font.render(label, True, (12, 19, 30))
    screen.blit(rendered, rendered.get_rect(center=rect.center))


running = True
while running:
    frame_dt = min(clock.tick(FPS) / 1000.0, 0.05)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for field in fields.values():
            field.event(event)

        if event.type == pygame.MOUSEWHEEL:
            mouse = pygame.mouse.get_pos()
            if mouse[0] < VIEW_W:
                anchor = to_world(mouse)
                scale = max(MIN_SCALE, min(MAX_SCALE, scale * ZOOM_FACTOR ** event.y))
                # Keep the physical point under the cursor fixed while zooming.
                camera = Vector2(
                    anchor.x - (mouse[0] - VIEW_W / 2) / scale,
                    anchor.y + (mouse[1] - WINDOW_H / 2) / scale,
                )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if apply_btn.collidepoint(event.pos) or reset_btn.collidepoint(event.pos):
                try:
                    if reset_btn.collidepoint(event.pos):
                        values = dict(DEFAULTS)
                        for key, field in fields.items():
                            field.set_value(values[key])
                    else:
                        values = {key: field.parse() for key, field in fields.items()}
                    start_simulation(values)
                    message = "Simulation restarted"
                    message_color = GREEN
                except ValueError as exc:
                    message = str(exc)
                    message_color = RED

        if event.type == pygame.KEYDOWN:
            any_editing = any(field.active for field in fields.values())
            if not any_editing:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_c:
                    camera = center_of_mass()

    if not paused:
        accumulator += frame_dt
        simulated_steps = 0
        while accumulator >= PHYSICS_DT and simulated_steps < MAX_PHYSICS_STEPS_PER_FRAME:
            try:
                step_velocity_verlet(bodies, PHYSICS_DT, params["G"])
            except (ValueError, ZeroDivisionError, OverflowError) as exc:
                paused = True
                message = f"Simulation stopped: {type(exc).__name__}"
                message_color = RED
                accumulator = 0.0
                break
            simulated_steps += 1
            steps_count += 1
            sim_time += PHYSICS_DT
            accumulator -= PHYSICS_DT
            if steps_count % TRAIL_EVERY == 0:
                for i, body in enumerate(bodies):
                    trails[i].append(body.position)
                    if len(trails[i]) > MAX_TRAIL_POINTS:
                        trails[i].pop(0)
        # Do not accumulate an unbounded backlog if the computer falls behind.
        if simulated_steps == MAX_PHYSICS_STEPS_PER_FRAME:
            accumulator = min(accumulator, PHYSICS_DT)

    screen.fill(BG)
    view_clip = pygame.Rect(0, 0, VIEW_W, WINDOW_H)
    screen.set_clip(view_clip)
    colors = (ACCENT, ORANGE)
    for i, body in enumerate(bodies):
        points = [to_screen(pos) for pos in trails[i]]
        if len(points) > 1:
            pygame.draw.lines(screen, colors[i], False, points, 2)
        pygame.draw.circle(screen, colors[i], to_screen(body.position), 11)
    pygame.draw.circle(screen, TEXT, to_screen(center_of_mass()), 4)
    screen.set_clip(None)

    # HUD in visualization area
    sep = (bodies[1].position - bodies[0].position).length()
    hud = [
        f"Time: {sim_time:.2f}s  |  FPS: {clock.get_fps():.0f}",
        f"Separation: {sep:.4f}  |  Zoom: {scale:.1f} px/unit",
        "Wheel: zoom  |  C: center on COM  |  Space: pause",
    ]
    for idx, line in enumerate(hud):
        screen.blit(small_font.render(line, True, TEXT), (15, 15 + 22 * idx))

    # Control panel
    pygame.draw.rect(screen, PANEL_BG, (VIEW_W, 0, PANEL_W, WINDOW_H))
    screen.blit(title_font.render("N-body Controls", True, TEXT), (VIEW_W + 18, 18))
    screen.blit(small_font.render("Initial conditions (2 bodies)", True, MUTED), (VIEW_W + 20, 57))
    for field in fields.values():
        field.draw()
    draw_button(apply_btn, "Apply", GREEN)
    draw_button(reset_btn, "Defaults", ACCENT)
    status = "PAUSED" if paused else "RUNNING"
    status_color = ORANGE if paused else GREEN
    screen.blit(font.render(status, True, status_color), (VIEW_W + 20, 584))
    # Clip feedback to panel width if needed
    feedback = small_font.render(message[:37], True, message_color)
    screen.blit(feedback, (VIEW_W + 20, 615))
    screen.blit(small_font.render("Changes apply on restart.", True, MUTED), (VIEW_W + 20, 651))
    screen.blit(small_font.render("Mass > 0; G >= 0", True, MUTED), (VIEW_W + 20, 677))

    pygame.display.flip()

pygame.quit()
