"""PyPhysics3D three-body sandbox with a Pygame-only parameter editor.

Place this file in examples/ and run from the repository root:
    python examples/three_body_2d_ui_clipboard.py

The UI changes initial conditions only. The physics engine remains authoritative:
    pyphysics.physics2d.gravity.integrator.step_velocity_verlet
"""

import math
import pygame

from pyphysics.math import Vector2
from pyphysics.physics2d.body import Body2D
from pyphysics.physics2d.gravity.integrator import step_velocity_verlet

WINDOW_W, WINDOW_H = 1320, 830
PANEL_W = 420
VIEW_W = WINDOW_W - PANEL_W
FPS = 60
PHYSICS_DT = 0.002
MAX_STEPS_PER_FRAME = 180
TRAIL_EVERY = 5
MAX_TRAIL_POINTS = 3500
ZOOM_FACTOR = 1.15
MIN_SCALE, MAX_SCALE = 3.0, 2500.0

BG = (12, 17, 30)
PANEL_BG = (24, 32, 49)
INPUT_BG = (37, 47, 66)
BORDER = (78, 95, 121)
TEXT = (232, 239, 249)
MUTED = (159, 174, 196)
BLUE = (95, 170, 255)
ORANGE = (255, 175, 80)
GREEN = (112, 221, 154)
RED = (255, 117, 124)
PURPLE = (190, 146, 255)
COLORS = (BLUE, ORANGE, PURPLE)
LABELS = ("A", "B", "C")

# These values are the exact initial conditions chosen for the experiment.
DEFAULTS = {
    "G": 1.0,
    "A m": 1.0, "A x": -1.0, "A y": 0.0, "A vx": 0.0, "A vy": 0.4,
    "B m": 1.0, "B x": 1.0, "B y": 0.0, "B vx": 0.0, "B vy": -0.4,
    "C m": 0.1, "C x": 0.0, "C y": 2.0, "C vx": 0.5, "C vy": 0.0,
}


def build_bodies(values):
    return [
        Body2D(
            position=Vector2(values[f"{name} x"], values[f"{name} y"]),
            velocity=Vector2(values[f"{name} vx"], values[f"{name} vy"]),
            mass=values[f"{name} m"],
        )
        for name in LABELS
    ]


def validate(values):
    if values["G"] < 0:
        raise ValueError("G must be >= 0")
    for name in LABELS:
        if values[f"{name} m"] <= 0:
            raise ValueError(f"Body {name}: mass must be > 0")
    # Our current gravity solver does not support coincident positions.
    if values["G"] > 0:
        for i, a in enumerate(LABELS):
            for b in LABELS[i + 1:]:
                if (values[f"{a} x"] == values[f"{b} x"] and
                        values[f"{a} y"] == values[f"{b} y"]):
                    raise ValueError(f"Bodies {a} and {b} overlap initially")


def center_of_mass(bodies):
    mass = sum(b.mass for b in bodies)
    weighted = Vector2(0.0, 0.0)
    for body in bodies:
        weighted = weighted + body.position * body.mass
    return weighted / mass


def momentum(bodies):
    p = Vector2(0.0, 0.0)
    for b in bodies:
        p = p + b.velocity * b.mass
    return p


def total_energy(bodies, g):
    kinetic = sum(0.5 * b.mass * b.velocity.dot(b.velocity) for b in bodies)
    potential = 0.0
    for i, a in enumerate(bodies):
        for b in bodies[i + 1:]:
            r = (b.position - a.position).length()
            if r == 0:
                return float("nan")
            potential -= g * a.mass * b.mass / r
    return kinetic + potential


def clipboard_copy(text):
    """Copy text to the system clipboard through Pygame's clipboard API."""
    try:
        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8") + b"\x00")
        return True
    except (pygame.error, OSError):
        return False


def clipboard_paste():
    """Get clipboard text, or return None if clipboard is unavailable."""
    try:
        content = pygame.scrap.get(pygame.SCRAP_TEXT)
        if content is None:
            return None
        return content.decode("utf-8-sig", errors="replace").split("\x00", 1)[0]
    except (pygame.error, OSError, UnicodeError):
        return None


class NumberInput:
    def __init__(self, label, rect, value):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.text = f"{value:.8g}"
        self.active = False
        self.invalid = False
        self.select_all = False

    def set_value(self, value):
        self.text = f"{value:.8g}"
        self.invalid = False
        self.active = False
        self.select_all = False

    def insert(self, content):
        # Numeric inputs accept only numeric syntax; validation happens on Apply/Enter.
        content = content.strip()
        if not content or any(c not in "0123456789+-.eE" for c in content):
            self.invalid = True
            return
        candidate = content if self.select_all else self.text + content
        if len(candidate) <= 24:
            self.text = candidate
            self.invalid = False
            self.select_all = False

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = self.rect.collidepoint(event.pos)
            if clicked and not self.active:
                self.select_all = True  # Convenient replacement of an existing value.
            if not clicked:
                self.select_all = False
            self.active = clicked
        elif event.type == pygame.KEYDOWN and self.active:
            ctrl = bool(event.mod & pygame.KMOD_CTRL)
            if ctrl and event.key == pygame.K_a:
                self.select_all = True
            elif ctrl and event.key == pygame.K_c:
                clipboard_copy(self.text)
            elif ctrl and event.key == pygame.K_x:
                if clipboard_copy(self.text):
                    self.text = ""
                    self.select_all = False
                    self.invalid = False
            elif ctrl and event.key == pygame.K_v:
                pasted = clipboard_paste()
                if pasted is not None:
                    self.insert(pasted)
            elif event.key == pygame.K_BACKSPACE:
                self.text = "" if self.select_all else self.text[:-1]
                self.select_all = False
                self.invalid = False
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB,
                               pygame.K_ESCAPE):
                self.active = False
                self.select_all = False
            elif not ctrl and event.unicode in "0123456789+-.eE" and event.unicode:
                self.insert(event.unicode)

    def parse(self):
        try:
            n = float(self.text)
            if not math.isfinite(n):
                raise ValueError
        except ValueError:
            self.invalid = True
            raise ValueError(f"{self.label}: enter a finite number") from None
        self.invalid = False
        return n

    def draw(self, surface, font, font_small):
        surface.blit(font_small.render(self.label, True, MUTED),
                     (self.rect.x, self.rect.y - 19))
        border = RED if self.invalid else BLUE if self.active else BORDER
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=5)
        pygame.draw.rect(surface, border, self.rect,
                         2 if self.active else 1, border_radius=5)
        display = self.text[-13:]
        if self.active and self.select_all:
            text_width = font.size(display)[0]
            pygame.draw.rect(surface, (62, 99, 153),
                             (self.rect.x + 7, self.rect.y + 5,
                              min(text_width + 3, self.rect.width - 13), self.rect.height - 10),
                             border_radius=2)
        cursor = "|" if self.active and not self.select_all and pygame.time.get_ticks() // 500 % 2 == 0 else ""
        img = font.render(display + cursor, True, TEXT)
        surface.blit(img, (self.rect.x + 8, self.rect.y + 7))


def draw_button(surface, font, rect, text, color):
    pygame.draw.rect(surface, color, rect, border_radius=7)
    img = font.render(text, True, BG)
    surface.blit(img, img.get_rect(center=rect.center))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    try:
        pygame.scrap.init()
    except pygame.error:
        pass  # The rest of the simulation still works without a clipboard.
    pygame.display.set_caption("PyPhysics3D | Three-body Lab")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 17)
    small = pygame.font.SysFont("consolas", 14)
    title = pygame.font.SysFont("consolas", 25, bold=True)
    heading = pygame.font.SysFont("consolas", 19, bold=True)

    panel_x = VIEW_W + 18
    input_w, col_step = 117, 130
    fields = {"G": NumberInput("G", (panel_x, 112, input_w, 32), DEFAULTS["G"])}
    section_y = {"A": 184, "B": 347, "C": 510}
    for name in LABELS:
        y0 = section_y[name]
        for i, key in enumerate(("m", "x", "y", "vx", "vy")):
            row, col = divmod(i, 3)
            label = f"{name} {key}"
            x = panel_x + col * col_step
            y = y0 + 37 + row * 56
            fields[label] = NumberInput(label, (x, y, input_w, 31), DEFAULTS[label])

    # Live simulation speed control; changes the simulated time per real second,
    # NOT the Velocity Verlet integration step.
    speed_min, speed_max = 0.25, 20.0
    simulation_speed = 1.0
    speed_dragging = False
    slider_rect = pygame.Rect(panel_x + 9, 785, 360, 12)
    speed_input = NumberInput("Speed (x)", (panel_x + 278, 738, 102, 32), simulation_speed)
    speed_ticks = (0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0)

    def speed_from_mouse(mouse_x):
        fraction = max(0.0, min(1.0, (mouse_x - slider_rect.left) / slider_rect.width))
        # Logarithmic scale gives useful precision at both low and high speeds.
        return speed_min * (speed_max / speed_min) ** fraction

    def speed_to_fraction(speed):
        return math.log(speed / speed_min) / math.log(speed_max / speed_min)

    def commit_speed_input():
        nonlocal simulation_speed, status_message, status_color
        try:
            value = speed_input.parse()
            if not (speed_min <= value <= speed_max):
                raise ValueError(f"Speed must be {speed_min:g} to {speed_max:g}x")
            simulation_speed = value
            speed_input.set_value(simulation_speed)
            status_message = "Simulation speed updated"
            status_color = GREEN
        except ValueError as exc:
            speed_input.invalid = True
            status_message = str(exc)
            status_color = RED

    apply_rect = pygame.Rect(panel_x, 677, 184, 39)
    default_rect = pygame.Rect(panel_x + 203, 677, 177, 39)
    params = dict(DEFAULTS)
    bodies = build_bodies(params)
    trails = [[b.position] for b in bodies]
    initial_energy = total_energy(bodies, params["G"])
    paused = False
    running = True
    follow_com = False
    middle_dragging = False
    camera = Vector2(0, 0)
    scale = 145.0
    sim_time = 0.0
    accumulator = 0.0
    step_count = 0
    status_message = "Edit values and click Apply"
    status_color = MUTED

    def to_screen(p):
        return (int(VIEW_W / 2 + (p.x - camera.x) * scale),
                int(WINDOW_H / 2 - (p.y - camera.y) * scale))

    def to_world(pixel):
        return Vector2(camera.x + (pixel[0] - VIEW_W / 2) / scale,
                       camera.y - (pixel[1] - WINDOW_H / 2) / scale)

    def restart(values):
        nonlocal params, bodies, trails, initial_energy, paused
        nonlocal sim_time, accumulator, step_count, camera
        validate(values)
        new_bodies = build_bodies(values)
        params = values
        bodies = new_bodies
        trails = [[b.position] for b in bodies]
        initial_energy = total_energy(bodies, params["G"])
        sim_time = accumulator = 0.0
        step_count = 0
        paused = False
        camera = center_of_mass(bodies) if follow_com else Vector2(0, 0)

    while running:
        frame_dt = min(clock.tick(FPS) / 1000.0, 0.05)
        # Avoid a stuck drag if middle mouse button was released outside window.
        if middle_dragging and not pygame.mouse.get_pressed(3)[1]:
            middle_dragging = False
        if speed_dragging and not pygame.mouse.get_pressed(3)[0]:
            speed_dragging = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            for field in fields.values():
                field.handle(event)
            was_speed_active = speed_input.active
            speed_input.handle(event)
            if was_speed_active and not speed_input.active:
                # Enter, Tab, Escape or clicking outside commits the typed value.
                commit_speed_input()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if slider_rect.inflate(12, 24).collidepoint(event.pos):
                    speed_dragging = True
                    simulation_speed = speed_from_mouse(event.pos[0])
                    speed_input.set_value(simulation_speed)
                elif apply_rect.collidepoint(event.pos) or default_rect.collidepoint(event.pos):
                    try:
                        if default_rect.collidepoint(event.pos):
                            new_values = dict(DEFAULTS)
                            for key, field in fields.items():
                                field.set_value(new_values[key])
                        else:
                            new_values = {key: field.parse() for key, field in fields.items()}
                        restart(new_values)
                        status_message = "Initial conditions applied"
                        status_color = GREEN
                    except ValueError as exc:
                        status_message = str(exc)
                        status_color = RED

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                speed_dragging = False

            elif event.type == pygame.MOUSEMOTION and speed_dragging:
                simulation_speed = speed_from_mouse(event.pos[0])
                speed_input.set_value(simulation_speed)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                # Start camera panning only inside the simulation viewport.
                if event.pos[0] < VIEW_W:
                    middle_dragging = True
                    follow_com = False

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                middle_dragging = False

            elif event.type == pygame.MOUSEMOTION and middle_dragging:
                # Move the camera opposite to mouse movement in world units.
                dx, dy = event.rel
                camera = Vector2(camera.x - dx / scale,
                                 camera.y + dy / scale)

            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if mx < VIEW_W:
                    if follow_com:
                        camera = center_of_mass(bodies)
                    anchor = to_world((mx, my))
                    scale = max(MIN_SCALE, min(MAX_SCALE, scale * ZOOM_FACTOR ** event.y))
                    camera = Vector2(
                        anchor.x - (mx - VIEW_W / 2) / scale,
                        anchor.y + (my - WINDOW_H / 2) / scale,
                    )
                    # Free camera after cursor-anchored zoom so the anchor stays fixed.
                    follow_com = False

            elif event.type == pygame.KEYDOWN and not (any(f.active for f in fields.values()) or speed_input.active):
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    restart(dict(params))
                elif event.key == pygame.K_t:
                    trails = [[b.position] for b in bodies]
                elif event.key == pygame.K_c:
                    follow_com = not follow_com
                    if follow_com:
                        camera = center_of_mass(bodies)

        if not paused:
            accumulator += frame_dt * simulation_speed
            steps_this_frame = 0
            while accumulator >= PHYSICS_DT and steps_this_frame < MAX_STEPS_PER_FRAME:
                try:
                    step_velocity_verlet(bodies, PHYSICS_DT, params["G"])
                    if not all(math.isfinite(n) for b in bodies for n in
                               (b.position.x, b.position.y, b.velocity.x, b.velocity.y)):
                        raise ValueError("Non-finite coordinates")
                except (ValueError, OverflowError, ZeroDivisionError) as exc:
                    paused = True
                    accumulator = 0.0
                    status_message = "Simulation stopped: " + str(exc)[:34]
                    status_color = RED
                    break
                accumulator -= PHYSICS_DT
                steps_this_frame += 1
                step_count += 1
                sim_time += PHYSICS_DT
                if step_count % TRAIL_EVERY == 0:
                    for i, b in enumerate(bodies):
                        trails[i].append(b.position)
                        if len(trails[i]) > MAX_TRAIL_POINTS:
                            trails[i].pop(0)
            if steps_this_frame == MAX_STEPS_PER_FRAME:
                accumulator = min(accumulator, PHYSICS_DT)

        com = center_of_mass(bodies)
        if follow_com:
            camera = com
        screen.fill(BG)
        screen.set_clip(pygame.Rect(0, 0, VIEW_W, WINDOW_H))
        for i, b in enumerate(bodies):
            points = [to_screen(p) for p in trails[i]]
            if len(points) >= 2:
                pygame.draw.lines(screen, COLORS[i], False, points, 2)
            pygame.draw.circle(screen, COLORS[i], to_screen(b.position), 12 if i < 2 else 9)
        pygame.draw.circle(screen, TEXT, to_screen(com), 4)
        screen.set_clip(None)

        current_energy = total_energy(bodies, params["G"])
        delta_e = (current_energy - initial_energy) / max(abs(initial_energy), 1e-12)
        p = momentum(bodies)
        pairs = []
        for i in range(3):
            for j in range(i + 1, 3):
                distance = (bodies[j].position - bodies[i].position).length()
                pairs.append(f"{LABELS[i]}{LABELS[j]}={distance:.3f}")
        hud = [
            f"THREE-BODY LAB    t={sim_time:.2f}s    FPS={clock.get_fps():.0f}    Speed target {simulation_speed:.2f}x",
            f"Zoom {scale:.1f}px/unit   Follow COM: {'ON' if follow_com else 'OFF'}",
            f"Total energy: {current_energy:.6g}    relative drift: {delta_e:+.2e}",
            f"Total momentum: ({p.x:.4f}, {p.y:.4f})",
            "Distances: " + "   ".join(pairs),
            "Wheel: zoom | Middle drag: pan | Space: pause | R: restart | C: COM | T: trails",
        ]
        for i, line in enumerate(hud):
            screen.blit(small.render(line, True, TEXT), (18, 15 + i * 23))

        pygame.draw.rect(screen, PANEL_BG, (VIEW_W, 0, PANEL_W, WINDOW_H))
        screen.blit(title.render("Three-body Controls", True, TEXT), (panel_x, 19))
        screen.blit(small.render("Initial conditions | Apply restarts simulation", True, MUTED),
                    (panel_x, 54))
        screen.blit(heading.render("Gravity", True, TEXT), (panel_x, 80))
        for i, name in enumerate(LABELS):
            y0 = section_y[name]
            pygame.draw.line(screen, BORDER, (panel_x, y0 - 10),
                             (WINDOW_W - 18, y0 - 10), 1)
            screen.blit(heading.render(f"Body {name}", True, COLORS[i]), (panel_x, y0))
        for field in fields.values():
            field.draw(screen, font, small)
        draw_button(screen, font, apply_rect, "Apply", GREEN)
        draw_button(screen, font, default_rect, "Defaults", BLUE)
        screen.blit(small.render("Simulation speed (live)", True, TEXT),
                    (panel_x, 747))
        speed_input.draw(screen, font, small)
        pygame.draw.rect(screen, BORDER, slider_rect, border_radius=6)
        fraction = speed_to_fraction(simulation_speed)
        filled_width = max(1, int(slider_rect.width * fraction))
        pygame.draw.rect(screen, BLUE,
                         (slider_rect.x, slider_rect.y, filled_width, slider_rect.height),
                         border_radius=6)
        # Tick positions correspond to logarithmic speed mapping.
        for tick in speed_ticks:
            tick_x = slider_rect.x + round(slider_rect.width * speed_to_fraction(tick))
            pygame.draw.line(screen, MUTED,
                             (tick_x, slider_rect.bottom + 3),
                             (tick_x, slider_rect.bottom + 9), 1)
            label = f"{tick:g}"
            label_img = small.render(label, True, MUTED)
            screen.blit(label_img,
                        (tick_x - label_img.get_width() // 2, slider_rect.bottom + 11))
        thumb_x = slider_rect.x + round(slider_rect.width * fraction)
        pygame.draw.circle(screen, TEXT, (thumb_x, slider_rect.centery), 10)
        state = "PAUSED" if paused else "RUNNING"
        # Surface validation / numerical errors in the panel without hiding controls.
        if status_color == RED:
            pygame.draw.rect(screen, PANEL_BG, (panel_x, 803, 390, 21))
            screen.blit(small.render(status_message[:48], True, RED), (panel_x, 805))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
