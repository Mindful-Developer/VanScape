import pygame
import math
import random
import os


pygame.init()
OBJ_RADIUS = 30


def draw_image_centered(win, img, x, y):
    w = img.get_width()
    h = img.get_height()
    win.blit(img, (x - w / 2, y - h / 2))


def load(which, scale_value):
    img = pygame.image.load(f'imgs/{which}.png').convert_alpha()
    w = scale_value * 2
    h = w * img.get_height() / img.get_width()
    return pygame.transform.scale(img, (w, h))


def random_corner():
    w = pygame.display.Info().current_w
    h = pygame.display.Info().current_h
    corners = (
        (0 - OBJ_RADIUS, 0 - OBJ_RADIUS),
        (0 - OBJ_RADIUS, h + OBJ_RADIUS),
        (w + OBJ_RADIUS, h + OBJ_RADIUS),
        (w + OBJ_RADIUS, 0 - OBJ_RADIUS)
    )
    return random.choice(corners)


class HemBullet:
    def __init__(self, x, y, radius, vel):
        self.x = x
        self.y = y
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.direction = math.atan2(mouse_y - self.y, mouse_x - self.x)
        self.radius = radius
        self.angle = 0
        self.vel = vel

    def draw(self, win):
        hemlock_rotated = pygame.transform.rotate(hemlock_img, self.angle)
        draw_image_centered(win, hemlock_rotated, self.x, self.y)

    def move(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = -math.degrees(math.atan2(mouse_y - self.y, mouse_x - self.x))
        self.x += self.vel * math.cos(self.direction)
        self.y += self.vel * math.sin(self.direction)

    def collide(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 <= (self.radius + other.radius) ** 2


class Strawberry:
    def __init__(self, x, y, radius, vel, direction):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel = vel
        self.direction = direction
        self.angle = random.randint(0, 360)

    def draw(self, win):
        img = pygame.transform.rotate(strawberry_img, self.angle)
        draw_image_centered(win, img, self.x, self.y)

    def move(self):
        self.x += self.vel * math.cos(self.direction)
        self.y += self.vel * math.sin(self.direction)
        self.angle += 1

    def collide(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 <= (self.radius + other.radius) ** 2

class Hamlet:
    def __init__(self, x, y, radius, vel, bullets):
        self.x = x
        self.y = y
        self.bullets = bullets
        self.radius = radius
        self.vel = vel * 2
        self.angle = 0
        self.destination_x, self.destination_y = pygame.mouse.get_pos()
        self.direction = math.atan2(self.destination_y - self.y, self.destination_x - self.x)

    def draw(self, win):
        hamlet_rotated = pygame.transform.rotate(ham_img, self.angle)
        draw_image_centered(win, hamlet_rotated, self.x, self.y)

    def move(self):
        self.angle += 1
        self.x += self.vel * math.cos(self.direction)
        self.y += self.vel * math.sin(self.direction)
        if self.destination_x - self.radius < self.x < self.destination_x + self.radius:
            if self.destination_y - self.radius < self.y < self.destination_y + self.radius:
                self.explode()

    def explode(self):
        num_berries = random.randint(5, 20)
        for i in range(num_berries):
            strawberry = Strawberry(self.x, self.y, self.radius // 2, self.vel, 360 // num_berries * i)
            self.bullets.append(strawberry)
        self.bullets.remove(self)

    def collide(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 <= (self.radius + other.radius) ** 2


class Enemy:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel = 0.25
        self.level = 0
        self.angle = 0
        self.bullets = []
        self.img = load("van", radius)
        self.bullet_size = radius // 2

    def draw(self, win):
        img = pygame.transform.rotate(self.img, math.degrees(-self.angle))
        draw_image_centered(win, img, self.x, self.y)

    def move(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        self.angle = angle
        self.x += (self.vel + self.level / 100 * 2) * math.cos(angle)
        self.y += (self.vel + self.level / 100 * 2) * math.sin(angle)
        if random.random() < 0.01:
            self.shoot(win)

    def shoot(self, win):
        bullet = HemBullet(self.x, self.y, self.bullet_size, self.vel)
        self.bullets.append(bullet)

    def ham_attack(self, win, bullets):
        ham = Hamlet(self.x, self.y, self.radius // 2, self.vel + self.level / 100 * 2, bullets)
        self.bullets.append(ham)

    def collide(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 <= (self.radius + other.radius) ** 2

    def reset(self, level=0):
        self.x, self.y = random_corner()
        self.level = level


class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.lives = 3
        self.imgs = [load(f"butterfly blue animation {num} 1200", radius) for num in range(1, 16)]
        self.img_index = 0
        self.counter = 10
        self.angle = 0

    def draw(self, win):
        rotated_butterfly = pygame.transform.rotate(self.imgs[self.img_index], math.degrees(self.angle))
        draw_image_centered(win, rotated_butterfly, self.x, self.y)
        font = pygame.font.SysFont('comicsans', 40)
        text = font.render("Lives: " + str(self.lives), 1, (255, 255, 255))
        win.blit(text, (WIDTH - 200, 10))

    def reset(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.x = mouse_x
        self.y = mouse_y
        self.lives = 3

    def move(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        d_x = mouse_x - self.x
        d_y = mouse_y - self.y
        if abs(d_x) + abs(d_y) > 4:
            self.angle = math.atan2(-d_y, d_x) - math.pi / 2
        self.x = mouse_x
        self.y = mouse_y
        self.counter -= 1
        if self.counter == 0:
            self.img_index += 1
            self.img_index %= len(self.imgs)
            self.counter = 10

    def collide(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 <= (self.radius + other.radius) ** 2


class Flower:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.extra_life = 1

    def draw(self, win):
        draw_image_centered(win, flower_img, self.x, self.y)

    def collide(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 <= (self.radius + other.radius) ** 2


class Score:
    def __init__(self):
        self.score = 0
        self.high_score = self.get_high_score()

    def get_high_score(self):
        if os.path.isfile("high_score.txt"):
            with open("high_score.txt", "r") as f:
                return int(f.read())
        else:
            with open("high_score.txt", "w") as f:
                f.write("0")
                return 0

    def draw(self, win):
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(f"Score: {str(self.score)}", 1, (255, 255, 255))
        text2 = font.render(f"Best: {self.high_score}", 1, (255, 255, 255))
        win.blit(text, (WIDTH // 2 - 100, 10))
        win.blit(text2, (10, 10))

    def update(self):
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score

    def reset(self):
        if self.high_score > self.get_high_score():
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        self.score = 0


class Game:
    def __init__(self):
        self.enemy = Enemy(*random_corner(), OBJ_RADIUS * 2)
        self.player = Player(WIDTH / 2, HEIGHT / 2, OBJ_RADIUS)
        self.score = Score()
        self.flowers = []

    def game_over_screen(self):
        win.fill((0, 0, 0))
        font = pygame.font.SysFont("comicsans", 40)
        font3 = pygame.font.SysFont("comicsans", 30)
        font2 = pygame.font.SysFont("comicsans", 20)
        text = font.render("Game Over", 1, (255, 0, 0))
        text_score = font3.render("Score: " + str(self.score.score), 1, (0, 255, 0))
        text2 = font2.render("Press 'ESC' to quit", 1, (255, 255, 255))
        text3 = font2.render("Press any other key to try again", 1, (255, 255, 255))
        win.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        win.blit(text_score, (WIDTH // 2 - 100, HEIGHT // 2))
        win.blit(text2, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
        win.blit(text3, (WIDTH // 2 - 100, HEIGHT // 2 + 80))
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                    self.reset()
                    self.run()

    def draw(self, win):
        for flower in self.flowers:
            flower.draw(win)
        self.player.draw(win)
        for bullet in self.enemy.bullets:
            bullet.draw(win)
        self.enemy.draw(win)
        self.score.draw(win)

    def update(self):
        self.enemy.move()
        self.player.move()
        self.score.update()
        for bullet_num in range(len(self.enemy.bullets) - 1, -1, -1):
            bullet = self.enemy.bullets[bullet_num]
            bullet.move()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                self.enemy.bullets.pop(bullet_num)

    def reset(self):
        self.enemy.reset()
        self.player.reset()
        self.score.reset()
        self.enemy.bullets = []

    def check_collision(self):
        if self.enemy.collide(self.player):
            self.player.lives -= 1
            if self.player.lives == 0:
                self.game_over_screen()
            else:
                current_enemy_lvl = self.enemy.level
                self.enemy.reset(level=current_enemy_lvl)
        for bullet in self.enemy.bullets:
            if bullet.collide(self.player):
                self.player.lives -= 1
                if self.player.lives == 0:
                    self.game_over_screen()
                self.enemy.bullets.remove(bullet)
        if self.flowers:
            for flower in self.flowers:
                if flower.collide(self.player):
                    self.player.lives += flower.extra_life
                    self.flowers.remove(flower)

    def check_score(self):
        if self.score.score % 500 == 0 and self.score.score != 0:
            self.enemy.level += 1
        if self.score.score % 1000 == 0 and self.score.score != 0:
            self.enemy.ham_attack(win, self.enemy.bullets)
        if self.score.score % 10000 == 0 and self.score.score != 0:
            self.flowers.append(Flower(random.randint(0, WIDTH), random.randint(0, HEIGHT), OBJ_RADIUS))

    @staticmethod
    def check_quit():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return True
        return False

    def run(self):
        run = True
        while run:
            if self.check_quit():
                run = False
            self.update()
            self.check_collision()
            self.check_score()
            # win.blit(grass_img, (0, 0))
            win.fill((0, 40, 0))
            self.draw(win)
            pygame.display.update()


if __name__ == "__main__":
    pygame.mouse.set_visible(False)
    WIDTH = pygame.display.Info().current_w
    HEIGHT = pygame.display.Info().current_h
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("VanScape")
    hemlock_img = load("hemlock", OBJ_RADIUS // 2)
    ham_img = load('ham', OBJ_RADIUS)
    strawberry_img = load("strawberry", OBJ_RADIUS // 2)
    flower_img = load("flower", OBJ_RADIUS)
    # grass_img = load("grass", 1080)

    game = Game()
    game.run()
    pygame.quit()
