import pygame
import math
from network import Network
from uuid import uuid4

pygame.init()


class Meteor():
    def __init__(self, position: tuple[int, int], size: int):
        self.pos = pygame.Vector2(position)
        self.size = size
        self.sprite = pygame.transform.scale(pygame.image.load(
            "assets/PNG/Meteors/meteorGrey_big1.png"), (self.size, self.size))
        self.rect = self.sprite.get_rect(topleft=self.pos)

    def draw(self, window):
        window.blit(self.sprite, self.pos)
        pygame.draw.rect(window, (255, 0, 0), self.rect, 1)


class Bullet():
    def __init__(self, position: tuple[int, int],
                 direction: float, bounces,
                 playerid):
        self.id = uuid4()
        self.pos = pygame.Vector2(position)
        self.direction = direction
        self.speed = 15
        self.velocity = pygame.Vector2(math.sin(self.direction)*self.speed,
                                       math.cos(self.direction)*self.speed)
        self.bounces = bounces
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 5, 5)
        self.playerid = playerid
        self.ally_sprite = pygame.transform.scale(pygame.image.load(
            "assets/PNG/Lasers/laserBlue08.png"), (10, 10))
        self.enemy_sprite = pygame.transform.scale(pygame.image.load(
            "assets/PNG/Lasers/laserGreen14.png"), (10, 10))

    def move_bullet(self):
        self.pos += self.velocity

    def draw_bullet(self, window, is_enemy: bool):
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        if is_enemy:
            sprite = self.enemy_sprite
        else:
            sprite = self.ally_sprite
        window.blit(sprite, (self.rect.x, self.rect.y))

    def bounce(self):
        self.bounces -= 1


class Player():

    def __init__(self, startx, starty, player_image, color=(255, 0, 0)):
        self.og_pos = [startx, starty]
        self.player_pos = pygame.Vector2(*self.og_pos[:])
        self.velocity = 4
        self.color = color
        self.og_player_image = player_image
        self.player_sprite = player_image
        self.rect = self.player_sprite.get_rect(center=(self.player_pos))
        self.current_angle = 0

    def draw(self, g):
        g.blit(self.player_sprite, (self.player_pos.x, self.player_pos.y))

    def move(self, dirn: tuple[int, int], meteors, dash_speed: float = 0):
        new_vector = pygame.Vector2(dirn).normalize()
        new_x = self.player_pos.x + (new_vector.x * self.velocity) + \
            (dash_speed * new_vector.x)
        new_y = self.player_pos.y + (new_vector.y * self.velocity) + \
            (dash_speed * new_vector.y)
        for meteor in meteors:
            if meteor.rect.colliderect(pygame.Rect(new_x, new_y, 50, 50)):
                return
        self.player_pos.update(new_x, new_y)
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

    def reset_pos(self):
        self.player_pos = pygame.Vector2(*self.og_pos[:])
        self.rect = self.player_sprite.get_rect(center=(self.player_pos))


class Game:

    def __init__(self, w, h, host):
        if host != "":
            self.net = Network(host)
        else:
            self.net = Network()
        self.width = w
        self.height = h
        self.FPS = 60
        self.canvas = Canvas(self.width, self.height, "Duel")
        self.player1_img = pygame.transform.scale(pygame.image.load(
            f"./assets/PNG/{self.net.playerSprite}.png").convert_alpha(), (50, 50))
        self.player2_img = pygame.transform.scale(pygame.image.load(
            f"./assets/PNG/{self.net.enemySprite}.png").convert_alpha(), (50, 50))
        self.player = Player(int(self.net.posPlayer[0]), int(
            self.net.posPlayer[1]), self.player1_img)
        self.player2 = Player(int(self.net.posEnemy[0]), int(
            self.net.posEnemy[1]), self.player2_img)
        self.bullets = []
        self.dash_cd = [5.0, 0.0, False]
        self.dash = 0
        self.available_bullets = 3
        self.reload_cd = [3.0, 0.0, False]
        self.bullet_icon = pygame.transform.scale(pygame.image.load(
            "assets/PNG/Lasers/laserBlue08.png"), (40, 40))
        self.bullet_icon_gray = pygame.transform.scale(pygame.image.load(
            "assets/PNG/Lasers/gray.jpg"), (40, 40))
        self.dash_icon = pygame.transform.rotate(pygame.transform.scale(
            pygame.image.load(
                "assets/PNG/UI/dash.png"), (40, 40)), 45)
        self.dash_icon_gray = pygame.transform.scale(pygame.image.load(
            "assets/PNG/UI/dash_gray.png"), (40, 40))
        self.score = [0, 0]
        self.game_state = "waiting_for_players"
        self.current_time = 0
        self.ready = [0, 0]
        self.meteors = []

    def run(self):
        clock = pygame.time.Clock()
        run = True
        self.meteors = [Meteor(
            (int(x[0]), int(x[1])),
            int(x[2])) for x in self.parse_meteors(self.net.send('5'))]

        while run:
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        if self.game_state != "game":
                            self.ready[int(self.net.id)] = \
                                0 if self.ready[int(self.net.id)] else 1
                        if self.available_bullets > 0 and \
                                self.game_state == "game":
                            self.available_bullets -= 1
                            if self.available_bullets == 0:
                                self.reload_cd[2] = True
                                self.reload_cd[1] = self.current_time
                            self.bullets.append(
                                Bullet(
                                    self.player.rect.center,
                                    math.radians(
                                        self.player.current_angle + 180),
                                    3, self.net.id))

            self.game_state = self.send_game_state()
            self.canvas.draw_background()
            if self.game_state == "game":
                self.ready = [0, 0]
                self.game()
            elif self.game_state == "waiting_for_players":
                self.canvas.draw_text(
                    "Waiting for players", 48, self.width/2, self.height/2)
            elif self.game_state == "game_over_winner":
                if self.score[int(self.net.id)] == 4:
                    self.canvas.draw_text(
                        "You won!", 48, self.width/2, self.height/2)
                else:
                    self.score[0 if int(self.net.id) else 1] += 1
                    self.canvas.draw_text(
                        "You lost!", 48, self.width/2, self.height/2)

            elif self.game_state == "game_over":
                self.bullets = []
                self.player.reset_pos()
                self.player2.reset_pos()
                self.available_bullets = 3
                self.meteors = [Meteor(
                                    (int(x[0]), int(x[1])),
                                    int(x[2])) for x in self.parse_meteors(
                                        self.net.send('5'))]

                self.canvas.draw_text(
                    "Game Over", 48, self.width/2, self.height/2)
                self.canvas.draw_text(
                    "Ready" if self.ready[0] else "Not Ready",
                    36, self.width/2-150, self.height/2+50)
                self.canvas.draw_text(
                    "Ready" if self.ready[1] else "Not Ready",
                    36, self.width/2+150, self.height/2+50)
                self.ready = self.parse_ready(self.send_ready())

            self.canvas.update()

        pygame.quit()

    def game(self):
        self.current_time = pygame.time.get_ticks() / 1000
        if self.dash_cd[2]:
            if self.current_time - self.dash_cd[1] >= self.dash_cd[0]:
                self.dash_cd[2] = False
        if self.reload_cd[2]:
            if self.current_time - self.reload_cd[1] >= self.reload_cd[0]:
                self.reload_cd[2] = False
                self.available_bullets = 3

        self.player.look_at_mouse()

        keys = pygame.key.get_pressed()
        if self.dash != 0:
            self.dash -= 1

        move_dir = [0, 0]
        if keys[pygame.K_d]:
            if self.player.player_pos.x <= self.width \
                    - self.player.velocity - 50:
                move_dir[0] = 1

        if keys[pygame.K_a]:
            if self.player.player_pos.x >= self.player.velocity:
                move_dir[0] = -1

        if keys[pygame.K_w]:
            if self.player.player_pos.y >= self.player.velocity:
                move_dir[1] = -1
        if keys[pygame.K_s]:
            if self.player.player_pos.y <= \
                    self.height - self.player.velocity - 50:
                move_dir[1] = 1

        if move_dir != [0, 0]:

            if keys[pygame.K_SPACE] and not self.dash_cd[2]:
                self.dash = 20
                self.dash_cd[1] = float(self.current_time)
                self.dash_cd[2] = True
            self.player.move(tuple(move_dir), self.meteors, self.dash)
            move_dir = [0, 0]

        # Collisions
        filtered_bullets = [b.rect for b in filter(
            self.check_if_enemy_bullet, self.bullets)]
        colliding = self.player2.rect.collidelistall(filtered_bullets)
        if len(colliding) > 0:
            self.score[int(self.net.id)] += 1
            self.game_state = "hit"
            # self.net.send("3:"+str(self.net.id))

        # Send Network Stuff
        self.player2.player_pos.x, self.player2.player_pos.y, \
            self.player2.current_angle = \
            self.parse_data(self.send_player_pos())
        self.player2.rotate(self.player2.current_angle)
        self.player2.rect = self.player2.player_sprite.get_rect(topleft=(
            self.player2.player_pos))
        self.score = self.parse_score(self.send_score())
        for j, bullet_list in enumerate(self.parse_bullets(
                self.send_bullets())):
            for i, data in enumerate(bullet_list):
                if not data:
                    continue
                data = data.split(",")
                if len(self.bullets) <= i:
                    self.bullets.append(
                        Bullet((int(data[0]),
                                int(data[1])), float(data[2]),
                               int(data[3]), j))
                else:
                    self.bullets[i].pos = pygame.Vector2(int(data[0]),
                                                         int(data[1]))
                    self.bullets[i].direction = float(data[2])
                    self.bullets[i].bounces = int(data[3])

        # Update Canvas
        self.player.draw(self.canvas.get_canvas())
        self.player2.draw(self.canvas.get_canvas())
        for meteor in self.meteors:
            meteor.draw(self.canvas.get_canvas())
        self.canvas.draw_text(f"{self.score[0]} : {self.score[1]}",
                              36,  int(self.width/2), 20)
        self.canvas.get_canvas().blit(
            self.dash_icon_gray if self.dash_cd[2] else self.dash_icon,
            (self.width - 60, 60))
        for i in range(3):
            i = i + 1
            if i > self.available_bullets:
                self.canvas.get_canvas().blit(
                    self.bullet_icon_gray, (self.width - 40 * i, 10))
            else:
                self.canvas.get_canvas().blit(
                    self.bullet_icon, (self.width - 40 * i, 10))

        for bullet in self.bullets:
            bullet.move_bullet()
            bullet.draw_bullet(self.canvas.get_canvas(), False
                               if bullet.playerid == self.net.id
                               else True)
            if bullet.pos.x < 0 or bullet.pos.x > \
                    self.width:
                bullet.bounce()
                bullet.velocity.x *= -1
            if bullet.pos.y < 0 \
                    or bullet.pos.y > self.height:
                bullet.bounce()
                bullet.velocity.y *= -1
            if m_list := bullet.rect.collidelistall(self.meteors):
                collide_tolerance = 8
                meteor = m_list[0]
                if abs(self.meteors[meteor].rect.top - bullet.rect.top
                       ) < collide_tolerance:
                    bullet.bounce()
                    bullet.velocity.y *= -1
                if abs(self.meteors[meteor].rect.bottom - bullet.rect.bottom
                       ) < collide_tolerance:
                    bullet.bounce()
                    bullet.velocity.y *= -1
                if abs(self.meteors[meteor].rect.left - bullet.rect.left
                       ) < collide_tolerance:
                    bullet.bounce()
                    bullet.velocity.x *= -1
                if abs(self.meteors[meteor].rect.right - bullet.rect.right
                       ) < collide_tolerance:
                    bullet.bounce()
                    bullet.velocity.x *= -1

            if bullet.bounces <= 0:
                self.bullets.remove(bullet)

    def check_if_enemy_bullet(self, bullet):
        return bullet.playerid == self.net.id

    def recharge_dash(self):
        self.can_dash = True

    # Function for sending data to server

    def send_game_state(self):
        data = f"3:{self.game_state}:{self.net.id}"
        reply = self.net.send(data)
        return reply

    def send_bullets(self):
        data = "2:"+str(self.net.id)+":"
        for bullet in self.bullets:
            if bullet.playerid != self.net.id:
                continue
            data += str(int(bullet.pos.x)) + ',' + str(int(bullet.pos.y)) \
                + ',' + str(
                bullet.direction) + ',' + str(bullet.bounces) + ';'
        reply = self.net.send(data)
        return reply

    def send_player_pos(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(int(self.player.player_pos.x)) + \
            "," + str(int(self.player.player_pos.y)) + \
            "," + str(self.player.current_angle)
        reply = self.net.send(data)
        return reply

    def send_score(self):
        data = "4:"+str(self.net.id)+":"+str(self.score[int(self.net.id)])
        reply = self.net.send(data)
        return reply

    def send_ready(self):
        data = "6:"+str(self.net.id)+":"+str(self.ready[int(self.net.id)])
        reply = self.net.send(data)
        return reply
    # Function to parse data which is coming from server

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1]), int(d[2])
        except Exception as exception:
            print(exception)
            return 0, 0, 0

    @staticmethod
    def parse_bullets(data):
        try:
            d = data.split(":")
            return [d[0].split(";"), d[1].split(";")]
        except Exception as exception:
            print(exception)
            return []

    @staticmethod
    def parse_score(data):
        try:
            d = data.split(":")
            return [int(d[0]), int(d[1])]
        except Exception as exception:
            print(exception)
            return [0, 0]

    @staticmethod
    def parse_game_state(data):
        try:
            d = data.split(":")
            if len(d) == 3:
                return d[0], int(d[1]), int(d[2])
            return d[0]
        except Exception as exception:
            print(exception)
            return "game"

    @staticmethod
    def parse_ready(data):
        try:
            d = data.split(":")
            return [int(d[0]), int(d[1])]
        except Exception as exception:
            print(exception)
            return [0, 0]

    @staticmethod
    def parse_meteors(data):
        try:
            d = data.split(":")
            return [x.split(",") for x in d]
        except Exception as exception:
            print(exception)
            return []


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
        render = font.render(text, True, (255, 255, 255))
        centerx = x - render.get_width() / 2
        centery = y - render.get_height() / 2
        self.screen.blit(render, (centerx, centery))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        bg_image = pygame.image.load("./assets/Backgrounds/black.png")
        bg_image_resized = pygame.transform.scale(
            bg_image, (self.width, self.height))
        self.screen.blit(bg_image_resized, (0, 0))
