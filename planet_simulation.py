import pygame, math, os, sys, random
pygame.init()
icon = pygame.image.load("planet_simulation_app_icon.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Planet Simulation")

WIDTH =  1250
HEIGHT = (2/3) * WIDTH
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
WHITE = (255,255,255)
LIGHT_ORANGE= (255,213,128)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
TAN = (210,180,140)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
BLACK = (22,22,24)
FONT = pygame.font.SysFont("comicsans", int((16/1500)*WIDTH))
font = pygame.font.Font(None, int((WIDTH/31.25)))
FRAMERATE = 60

class Planet:
    AU = 149.6e9
    G = 6.67428e-11
    SCALE = ((1/6) * WIDTH) / AU
    TIMESTEP = 3600  # 1 hour
    MAX_TRAIL_LENGTH = 10000  # number of points for fading trail

    def __init__(self, x, y, radius, color, mass, name, rings=False, moons=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.name = str(name)
        self.rings = rings 
        self.moons = moons or []

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0
        

    def draw(self, win, offset_x=WIDTH/3, offset_y=HEIGHT/2, zoom=1.2):
        x = self.x * self.SCALE * zoom + offset_x
        y = self.y * self.SCALE * zoom + offset_y

        if len(self.orbit) > 1:
            # Transparent surface for fading trail
            trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

            for i in range(1, len(self.orbit)):
                start_pos = (
                    self.orbit[i-1][0] * self.SCALE * zoom + offset_x,
                    self.orbit[i-1][1] * self.SCALE * zoom + offset_y
                )
                end_pos = (
                    self.orbit[i][0] * self.SCALE * zoom + offset_x,
                    self.orbit[i][1] * self.SCALE * zoom + offset_y
                )

                # Fade older points (younger = brighter)
                alpha = int(255 * (i / len(self.orbit)))
                color = (*self.color[:3], alpha)

                pygame.draw.line(trail_surface, color, start_pos, end_pos, 2)

            win.blit(trail_surface, (0, 0))

        
        # Draw planet itself
        pygame.draw.circle(win, self.color, (int(x), int(y)), max(1, int(self.radius * zoom)))

        if self.rings:
            radius = self.radius * 2.5 * zoom
            ring_rect = pygame.Rect(int(x - radius), int(y - radius/4), int(radius*2), int(radius/2))
            pygame.draw.ellipse(win, (200, 200, 200), ring_rect, 2)

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets, timestep=None):
        if timestep is None:
            timestep = self.TIMESTEP

        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * timestep
        self.y_vel += total_fy / self.mass * timestep

        self.x += self.x_vel * timestep
        self.y += self.y_vel * timestep

        self.orbit.append((self.x, self.y))

        # Limit trail length
        if len(self.orbit) > self.MAX_TRAIL_LENGTH:
            self.orbit.pop(0)
    
    def screen_position(self, offset_x, offset_y, zoom):
        x = self.x * self.SCALE * zoom + offset_x
        y = self.y * self.SCALE * zoom + offset_y
        return x, y
    
def main():
    run = True
    clock = pygame.time.Clock()
    paused = False  # Variable to track pause state
    NUM_STARS = random.randint(100, 200)
    stars = []
    
    # Zoom and pan variables
    zoom = 1
    offset_x = WIDTH/2
    offset_y = HEIGHT/2
    pan_speed = 20
    dragging = False
    last_mouse_pos = (0, 0)
    focused_planet = None 

    simulated_seconds = 0


    for _ in range(NUM_STARS):
        x = random.randint(0, WIDTH)
        y = random.randint(0, int(HEIGHT))
        radius = random.randint(1, 3)
        brightness = random.randint(150, 255)
        stars.append({"x": x, "y": y, "radius": radius, "brightness": brightness})

    SUN_RADIUS = int(WIDTH * 0.02) 
    EARTH_RADIUS = int(SUN_RADIUS/190)
    MARS_RADIUS = int(SUN_RADIUS/207)
    MERCURY_RADIUS = int(SUN_RADIUS/285)
    VENUS_RADIUS = int(SUN_RADIUS/115)
    JUPITER_RADIUS = int(SUN_RADIUS/10)
    SATURN_RADIUS = int(SUN_RADIUS/12)
    URANUS_RADIUS = int(SUN_RADIUS/27)
    NEPTUNE_RADIUS = int(SUN_RADIUS/28)
    PLUTO_RADIUS = int(SUN_RADIUS/585)

    # Create planets
    sun = Planet(0, 0, SUN_RADIUS, YELLOW, 1.98892e30, "SUN")
    sun.sun = True

    mercury = Planet(0.387 * Planet.AU, 0, MERCURY_RADIUS, DARK_GREY, 3.30e23, "MERCURY")
    mercury.y_vel = -47.4e3

    venus = Planet(0.723 * Planet.AU, 0, VENUS_RADIUS, LIGHT_ORANGE, 4.867e24, "VENUS")
    venus.y_vel = -35.02e3

    earth = Planet(-1 * Planet.AU, 0, EARTH_RADIUS, BLUE, 5.972e24, "EARTH")
    earth.y_vel = 29.783e3

    mars = Planet(-1.524 * Planet.AU, 0, MARS_RADIUS, RED, 6.39e23, "MARS")
    mars.y_vel = 24.077e3

    jupiter = Planet(5.204 * Planet.AU, 0, JUPITER_RADIUS, ORANGE, 1.898e27, "JUPITER")
    jupiter.y_vel = -13.07e3

    saturn = Planet(9.582 * Planet.AU, 0, SATURN_RADIUS, TAN, 5.683e26, "SATURN", rings=True)
    saturn.y_vel = -9.69e3

    uranus = Planet(19.201 * Planet.AU, 0, URANUS_RADIUS, CYAN, 8.681e25, "URANUS")
    uranus.y_vel = -6.81e3

    neptune = Planet(30.047 * Planet.AU, 0, NEPTUNE_RADIUS, BLUE, 1.024e26, "NEPTUNE")
    neptune.y_vel = -5.43e3

    pluto = Planet(39.48 * Planet.AU, 0, PLUTO_RADIUS, TAN, 1.309e22, "PLUTO")
    pluto.y_vel = -4.74e3

    # lebron = Planet(48.48 * Planet.AU, 0, PLUTO_RADIUS, TAN, 1.309 * 10**22, "LEBRON")
    # pluto.y_vel = -10.74 * 1000

    planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, pluto]

    def draw_gradient(win, color_top, color_bottom):
        """Draws a vertical gradient from color_top to color_bottom."""
        for y in range(int(HEIGHT)):
            # Interpolate each RGB channel
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * (y / HEIGHT))
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * (y / HEIGHT))
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * (y / HEIGHT))
            pygame.draw.line(win, (r, g, b), (0, y), (WIDTH, y))

    while run:
        clock.tick(FRAMERATE)
        draw_gradient(WIN, (0, 0, 0), (25, 25, 25))

        if focused_planet:
            px, py = focused_planet.screen_position(0, 0, zoom)
            target_x = WIDTH/2 - px
            target_y = HEIGHT/2 - py

            # Linear interpolation (smooth movement)
            lerp_factor = 1  # smaller = slower, smoother
            offset_x += (target_x - offset_x) * lerp_factor
            offset_y += (target_y - offset_y) * lerp_factor


        for star in stars:
            brightness = random.randint(150, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(WIN, color, (star["x"], star["y"]), star["radius"])

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Start dragging with left mouse button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                if event.button == 1:  # left click
                    dragging = True
                    last_mouse_pos = event.pos

                    # Check top buttons
                    for rect, action in button_rects:
                        if rect.collidepoint(mouse_x, mouse_y):
                            action()

                    clicked_planet = None
                    for planet in planets:
                        px, py = planet.screen_position(offset_x, offset_y, zoom)
                        if math.hypot(mouse_x - px, mouse_y - py) <= max(5, planet.radius * zoom):
                            clicked_planet = planet
                            break
                    
                    if clicked_planet:
                        if focused_planet == clicked_planet:
                            focused_planet = None
                        else:
                            focused_planet = clicked_planet
                    else:
                        focused_planet = None

                # Scroll zoom (trackpad pinch or scroll wheel)
                elif event.button == 4:  # scroll up
                    zoom_factor = 1.1
                    offset_x = mouse_x - (mouse_x - offset_x) * zoom_factor
                    offset_y = mouse_y - (mouse_y - offset_y) * zoom_factor
                    zoom *= zoom_factor
                elif event.button == 5:  # scroll down
                    zoom_factor = 1 / 1.1
                    offset_x = mouse_x - (mouse_x - offset_x) * zoom_factor
                    offset_y = mouse_y - (mouse_y - offset_y) * zoom_factor
                    zoom *= zoom_factor

            # Stop dragging
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            # Drag motion
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    offset_x += dx
                    offset_y += dy
                    last_mouse_pos = event.pos

            # Keyboard panning (optional)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    offset_x += pan_speed
                elif event.key == pygame.K_d:
                    offset_x -= pan_speed
                elif event.key == pygame.K_w:
                    offset_y += pan_speed
                elif event.key == pygame.K_s:
                    offset_y -= pan_speed


                # Check for button clicks (unchanged)
                # (same as original code below)
                # Increase / Decrease speed / Pause / Restart
                increase_speed_rect = pygame.Rect((8/15) * WIDTH, (1/100) * WIDTH, (1/10) * WIDTH, (5/100) * WIDTH)
                decrease_speed_rect = pygame.Rect((1/30) * WIDTH, (1/100) * WIDTH, (1/10) * WIDTH, (5/100) * WIDTH)
                pause_speed_rect = pygame.Rect((4/15) * WIDTH, (1/100) * WIDTH, (5/100) * WIDTH, (5/100) * WIDTH)
                restart_rect = pygame.Rect((1/3) * WIDTH, (1/100) * WIDTH, (5/100) * WIDTH, (5/100) * WIDTH)

                if increase_speed_rect.collidepoint(mouse_x, mouse_y):
                    Planet.TIMESTEP *= 2
                elif decrease_speed_rect.collidepoint(mouse_x, mouse_y):
                    Planet.TIMESTEP /= 2
                elif pause_speed_rect.collidepoint(mouse_x, mouse_y):
                    paused = not paused
                elif restart_rect.collidepoint(mouse_x, mouse_y):
                    os.execl(sys.executable, sys.executable, *sys.argv)

        if not paused:
            # Determine number of sub-steps
            sub_steps = max(1, int(Planet.TIMESTEP / 3600))  # divide TIMESTEP into 1-hour chunks
            dt = Planet.TIMESTEP / sub_steps  # small timestep for each sub-step

            for _ in range(sub_steps):
                for planet in planets:
                    planet.update_position(planets, timestep = dt)
        
            simulated_seconds += Planet.TIMESTEP
            earth_days = simulated_seconds / (60 * 60 * 24)


        # Draw planets + detect hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_planet = None

        for planet in planets:
            planet.draw(WIN, offset_x, offset_y, zoom)

            px, py = planet.screen_position(offset_x, offset_y, zoom)

            if math.hypot(mouse_x - px, mouse_y - py) <= max(5, planet.radius * zoom):
                hovered_planet = planet

                # Hover info popup
        
        # Hover info popup
        if hovered_planet is not None:
            info_font = pygame.font.SysFont("comicsans", 24)

            text_lines = [
                f"{hovered_planet.name}",
                f"Distance to Sun: {round(hovered_planet.distance_to_sun / Planet.AU, 3)} AU",
                f"Mass: {hovered_planet.mass:.2e} kg",
                f"Speed: {math.hypot(hovered_planet.x_vel, hovered_planet.y_vel):.1f} m/s"
            ]

            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Bigger box
            box_width = max(info_font.render(line, True, WHITE).get_width() for line in text_lines) + 40
            box_height = len(text_lines) * 30 + 20

            pygame.draw.rect(WIN, (25, 25, 25), (mouse_x + 15, mouse_y + 15, box_width, box_height), border_radius=8)
            pygame.draw.rect(WIN, WHITE, (mouse_x + 15, mouse_y + 15, box_width, box_height), 2, border_radius=8)

            y_offset = mouse_y + 30
            for line in text_lines:
                surf = info_font.render(line, True, WHITE)
                WIN.blit(surf, (mouse_x + 35, y_offset))
                y_offset += 30

        def toggle_pause():
            nonlocal paused
            paused = not paused
        
        top_buttons = [
            {"label": "- SPEED", "action": lambda: setattr(Planet, "TIMESTEP", Planet.TIMESTEP / 2)},
            {"label": "PAUSE/RESUME", "action": lambda: toggle_pause()},
            {"label": "RESET", "action": lambda: os.execl(sys.executable, sys.executable, *sys.argv)},
            {"label": "+ SPEED", "action": lambda: setattr(Planet, "TIMESTEP", Planet.TIMESTEP * 2)}]

        num_buttons = len(top_buttons)
        spacing = WIDTH / (num_buttons + 1)  # equal horizontal spacing
        button_rects = []  # store rectangles for click detection

        for i, button in enumerate(top_buttons):
            text_surface = font.render(button["label"], True, WHITE)
            x_pos = spacing * (i + 1) - text_surface.get_width()/2
            y_pos = 10  # 10 px from top
            WIN.blit(text_surface, (x_pos, y_pos))

            # Store rect for click detection
            rect = pygame.Rect(x_pos, y_pos, text_surface.get_width(), text_surface.get_height())
            button_rects.append((rect, button["action"]))
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if event.button == 1:  # left click
                for rect, action in button_rects:
                    if rect.collidepoint(mouse_x, mouse_y):
                        action()  # run the corresponding action

        time_font = pygame.font.SysFont("comicsans", 24)
        time_text = time_font.render(f"Time Elapsed: {earth_days:.2f} Earth days", True, WHITE)
        WIN.blit(time_text, (20, 60))

        pygame.display.update()

    pygame.quit()

main()