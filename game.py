import pygame
import math
from network import Network

pygame.init()


class Player():
    width = height = 50

    def __init__(self, startx, starty, player_image, color=(255, 0, 0)):
        self.x = startx
        self.y = starty
        self.velocity = 4
        self.color = color
        self.og_player_image = pygame.transform.scale(
            player_image, (self.width, self.height))
        self.player_sprite = pygame.transform.scale(
            player_image, (self.width, self.height))
        self.rect = self.player_sprite.get_rect(center=(self.x, self.y))
        self.current_angle = 0

    def draw(self, g):
        g.blit(self.player_sprite, (self.x, self.y))

    def move(self, dirn):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :return: None
        """

        if dirn == 0:
            self.x += self.velocity
        elif dirn == 1:
            self.x -= self.velocity
        elif dirn == 2:
            self.y -= self.velocity
        else:
            self.y += self.velocity
        self.rect = self.player_sprite.get_rect(topleft=(self.x, self.y))

    def look_at_mouse(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate the angle between the player and the mouse
        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        angle = math.atan2(rel_y, rel_x)
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.current_angle = int(angle)-90

        # Rotate the player image
        self.rotate(self.current_angle)

    def rotate(self, angle):
        self.player_sprite = pygame.transform.rotate(
            self.og_player_image, angle)
        self.rect = self.player_sprite.get_rect(center=self.rect.center)


class Game:

    def __init__(self, w, h):
        self.net = Network()
        self.width = w
        self.height = h
        self.canvas = Canvas(self.width, self.height, "Duel")
        self.player = Player(int(self.net.posPlayer[0]), int(self.net.posPlayer[1]), pygame.image.load(
            "./assets/PNG/playerShip1_blue.png").convert_alpha())
        self.player2 = Player(int(self.net.posEnemy[0]), int(self.net.posEnemy[1]), pygame.image.load(
            "./assets/PNG/playerShip1_green.png").convert_alpha())

    def run(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False

            self.player.look_at_mouse()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_d]:
                if self.player.x <= self.width - self.player.velocity:
                    self.player.move(0)

            if keys[pygame.K_a]:
                if self.player.x >= self.player.velocity:
                    self.player.move(1)

            if keys[pygame.K_w]:
                if self.player.y >= self.player.velocity:
                    self.player.move(2)

            if keys[pygame.K_s]:
                if self.player.y <= self.height - self.player.velocity:
                    self.player.move(3)

            # Send Network Stuff
            self.player2.x, self.player2.y, self.player2.current_angle = self.parse_data(
                self.send_data())
            self.player2.rotate(self.player2.current_angle)

            # Update Canvas
            self.canvas.draw_background()
            self.player.draw(self.canvas.get_canvas())
            self.player2.draw(self.canvas.get_canvas())
            self.canvas.update()

        pygame.quit()

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(self.player.x) + \
            "," + str(self.player.y) + "," + str(self.player.current_angle)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1]), int(d[2])
        except:
            return 0, 0, 0


class Canvas:

    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", size)
        render = font.render(text, 1, (0, 0, 0))

        self.screen.draw(render, (x, y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        bg_image = pygame.image.load("./assets/Backgrounds/black.png")
        bg_image_resized = pygame.transform.scale(
            bg_image, (self.width, self.height))
        self.screen.blit(bg_image_resized, (0, 0))
