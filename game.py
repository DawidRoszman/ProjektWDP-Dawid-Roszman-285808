import pygame
import math
from network import Network

pygame.init()


class Bullet():
    def __init__(self, position: tuple[int, int], direction: float):
        self.pos = pygame.Vector2(position)
        self.direction = direction
        self.speed = 8
        self.bounces = 3
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 5, 5)

    def move_bullet(self):
        self.pos.y += math.cos(self.direction) * self.speed
        self.pos.x += math.sin(self.direction) * self.speed

    def draw_bullet(self, window):
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        pygame.draw.rect(window, (255, 255, 255), self.rect)

    def bounce(self):
        self.direction = -self.direction
        self.bounces -= 1


class Player():
    width = height = 50

    def __init__(self, startx, starty, player_image, color=(255, 0, 0)):
        self.player_pos = pygame.Vector2(startx, starty)
        self.velocity = 4
        self.color = color
        self.og_player_image = pygame.transform.scale(
            player_image, (self.width, self.height))
        self.player_sprite = pygame.transform.scale(
            player_image, (self.width, self.height))
        self.rect = self.player_sprite.get_rect(center=(self.player_pos))
        self.current_angle = 0

    def draw(self, g):
        g.blit(self.player_sprite, (self.player_pos.x, self.player_pos.y))

    def move(self, dirn):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :return: None
        """

        if dirn == 0:
            self.player_pos.x += self.velocity
        elif dirn == 1:
            self.player_pos.x -= self.velocity
        elif dirn == 2:
            self.player_pos.y -= self.velocity
        else:
            self.player_pos.y += self.velocity
        self.rect = self.player_sprite.get_rect(topleft=(self.player_pos))

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
        self.player = Player(int(self.net.posPlayer[0]), int(
            self.net.posPlayer[1]), pygame.image.load(
            "./assets/PNG/playerShip1_blue.png").convert_alpha())
        self.player2 = Player(int(self.net.posEnemy[0]), int(
            self.net.posEnemy[1]), pygame.image.load(
            "./assets/PNG/playerShip1_green.png").convert_alpha())
        self.bullets = []

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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        print("created bullet")
                        self.bullets.append(Bullet(self.player.rect.center, math.radians(self.player.current_angle + 180)))


            self.player.look_at_mouse()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_d]:
                if self.player.player_pos.x <= self.width - self.player.velocity:
                    self.player.move(0)

            if keys[pygame.K_a]:
                if self.player.player_pos.x >= self.player.velocity:
                    self.player.move(1)

            if keys[pygame.K_w]:
                if self.player.player_pos.y >= self.player.velocity:
                    self.player.move(2)

            if keys[pygame.K_s]:
                if self.player.player_pos.y <= self.height - self.player.velocity:
                    self.player.move(3)



            # Send Network Stuff
            self.player2.player_pos.x, self.player2.player_pos.y, self.player2.current_angle = self.parse_data(
                self.send_data())
            self.player2.rotate(self.player2.current_angle)

            # Update Canvas
            self.canvas.draw_background()
            self.player.draw(self.canvas.get_canvas())
            self.player2.draw(self.canvas.get_canvas())

            for bullet in self.bullets:
                bullet.move_bullet()
                bullet.draw_bullet(self.canvas.get_canvas())
                if bullet.rect.x < 0 or bullet.rect.x > self.width or bullet.rect.y < 0 or bullet.rect.y > self.height:
                    bullet.bounce()
                    if bullet.bounces <= 0:
                        self.bullets.remove(bullet)

            self.canvas.update()

        pygame.quit()

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(self.player.player_pos.x) + \
            "," + str(self.player.player_pos.y) + "," + str(self.player.current_angle)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1]), int(d[2])
        except Exception as exception:
            print(exception)
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
        render = font.render(text, True, (0, 0, 0))

        self.screen.blit(render, (x, y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        bg_image = pygame.image.load("./assets/Backgrounds/black.png")
        bg_image_resized = pygame.transform.scale(
            bg_image, (self.width, self.height))
        self.screen.blit(bg_image_resized, (0, 0))
