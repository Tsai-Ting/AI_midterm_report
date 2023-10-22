import pygame
import random
import math
from scipy.spatial import KDTree

pygame.init()

# define background
WIDTH = 1500  # screen width
HEIGHT = 900  # screen height
FPS = 30
# BOIDS
NUM = 700  # boids number
DISTANCE = 8  # collision dis
NEI_DIS = 65  # neighbor dis
COL_V = 9
ALI_V = 9
COH_V = 600
SPEED = 7
# OBSTACLE
OBS_DIS = 50  # OBSTACLE dis
# PREDATOR
PRE_DIS = 300
PRED_SPEED = SPEED*2
PRED_COH_V = 5
BOID_PRED_DIS = 15
# define color
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PINK = (255, 20, 147)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 76, 153)
LIGHT_BLUE = (209, 233, 255)
LIGHT_ORANGE = (235, 214, 214)

btn1_c = False  # 控制OBSTACLES的btn
btn2_c = False # 控制PREDATOR的btn
obstacles = []

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boids HW")
clock = pygame.time.Clock()

class Boid:
    # 設定初始位置以及速度
    def __init__(self):
        self.x = int(random.uniform(0, WIDTH))
        self.y = int(random.uniform(HEIGHT-30, 0))
        # v[0]->x   v[1]->y
        self.v = [random.uniform(-SPEED, SPEED), random.uniform(-SPEED, SPEED)]

    def update_boid(self, kdtree: KDTree, boids, obstacles, predator):

        # 取距離<NEI_DIS的為周圍同伴
        neighbor_indices = kdtree.query_ball_point((self.x, self.y), NEI_DIS)
        nei_boids = [boids[i] for i in neighbor_indices]

        # 檢查是否超出邊界
        if self.x < 0 : self.x = WIDTH
        elif self.x > WIDTH : self.x = 0
        if self.y < 0 : self.y = HEIGHT-30
        elif self.y > HEIGHT-30 : self.y = 0

        if len(nei_boids) != 0:
            # 計算群中心
            c_x = 0
            c_y = 0
            for nei_boid in nei_boids:
                c_x += nei_boid.x
                c_y += nei_boid.y
            c_x = c_x / len(nei_boids)
            c_y = c_y / len(nei_boids)

            # 計算平均速度
            avg_v = [0, 0]
            for nei_boid in nei_boids:
                avg_v[0] += nei_boid.v[0]
                avg_v[1] += nei_boid.v[1]
            avg_v[0] = avg_v[0] / len(nei_boids)
            avg_v[1] = avg_v[1] / len(nei_boids)

            # requirement1 : Separation(avoid collision)
            for nei_boid in nei_boids:
                dis = math.hypot(self.x - nei_boid.x, self.y - nei_boid.y)  # 計算與鄰居boid的距離
                if dis < DISTANCE and nei_boid != self:  # 若是距離<DISTANCE，則往鄰居所在位置的反方向駛離
                    self.v[0] -= (nei_boid.x - self.x) / COL_V
                    self.v[1] -= (nei_boid.y - self.y) / COL_V

            # requirement2 : Alignment
            self.v[0] += (avg_v[0] - self.v[0]) / ALI_V  # 朝向鄰居平均方向前進(鄰居速度-自己速度)
            self.v[1] += (avg_v[1] - self.v[1]) / ALI_V

            # requirement3 : Cohesion
            self.v[0] += (c_x - self.x) / COH_V  # 朝鄰居平均位置中心移動(鄰居位置-自己位置)
            self.v[1] += (c_y - self.y) / COH_V

        # 躲避障礙物
        for obstacle in obstacles:
            dis = math.hypot(self.x - obstacle[0], self.y - obstacle[1])
            if dis < OBS_DIS:  # 如果距離<OBS_DIS，則往障礙物反方向移動
                self.v[0] -= (obstacle[0] - self.x)
                self.v[1] -= (obstacle[1] - self.y)

        # 限制速度 避免速度過快或過慢
        speed = math.hypot(self.v[0], self.v[1])
        if speed > (SPEED * (2 ** 0.5)) or speed < SPEED:  # 如果速度>SPEED的根號2次方 or 速度<SPEED，則將速度調整為SPEED的根號1.5次方
            self.v[0] = (self.v[0] / speed) * (SPEED * (1.5 ** 0.5))
            self.v[1] = (self.v[1] / speed) * (SPEED * (1.5 ** 0.5))

        # 如果有獵食者
        if predator is not None:
            dis = math.hypot(self.x - predator.x, self.y - predator.y)
            if dis < BOID_PRED_DIS:
                self.v[0] = -self.v[0] * 5  # 如果有周圍有獵食者，以更快的速度且反方向逃離
                self.v[1] = -self.v[1] * 5

        # update position
        self.x += self.v[0]
        self.y += self.v[1]

    def draw(self):
        pygame.draw.circle(screen, LIGHT_ORANGE, (int(self.x), int(self.y)), 3)

class Predator:
    def __init__(self):
        self.x = int(random.uniform(0, WIDTH))
        self.y = int(random.uniform(HEIGHT-30, 0))
        # v[0]->x   v[1]->y
        self.v = [random.uniform(-SPEED, SPEED), random.uniform(-SPEED, SPEED)]

    def update_predator(self, kdtree: KDTree, boids, obstacles):
        # 取距離<PRE_DIS的為周圍同伴
        neighbor_indices = kdtree.query_ball_point((self.x, self.y), PRE_DIS)
        nei_boids = [boids[i] for i in neighbor_indices]

        # 超出邊界
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT - 30
        elif self.y > HEIGHT - 30:
            self.y = 0
        # 計算周圍獵物的群中心
        if len(nei_boids) != 0:
            # 計算獵物群中心
            c_x = 0
            c_y = 0
            for nei_boid in nei_boids:
                c_x += nei_boid.x
                c_y += nei_boid.y
            c_x = c_x / len(nei_boids)
            c_y = c_y / len(nei_boids)
            # cohesion
            self.v[0] += (c_x - self.x) / PRED_COH_V
            self.v[1] += (c_y - self.y) / PRED_COH_V

        # 躲避障礙物
        for obstacle in obstacles:
            dis = math.hypot(self.x - obstacle[0], self.y - obstacle[1])
            if dis < OBS_DIS:
                self.v[0] = -self.v[0]
                self.v[1] = -self.v[1]

        # 限制速度
        speed = math.hypot(self.v[0], self.v[1])
        if speed != PRED_SPEED:
            self.v[0] = (self.v[0] / speed) * PRED_SPEED
            self.v[1] = (self.v[1] / speed) * PRED_SPEED

        # update position
        self.x += self.v[0]
        self.y += self.v[1]

    def draw(self):
        pygame.draw.circle(screen, PINK, (int(self.x), int(self.y)), 8)

boids = [Boid() for _ in range(NUM)]
# 設定自型
font = pygame.font.SysFont("Arial", 30)
# 設定文字
btn1_text = font.render("OBSTACLES", True, LIGHT_BLUE)
btn1_text_c = font.render("NO OBSTACLES", True, LIGHT_BLUE)
# 設定按鈕1位置
btn1 = btn1_text_c.get_rect(center=(WIDTH//3, HEIGHT-15))
# 設定文字
btn2_text = font.render("PREDATOR", True, LIGHT_BLUE)
btn2_text_c = font.render("NO PREDATOR", True, LIGHT_BLUE)
# 設定按鈕2位置
btn2 = btn2_text_c.get_rect(center=(WIDTH*2//3, HEIGHT-15))

# 主迴圈
running = True
while running:
    boids_positions = [(boid.x, boid.y) for boid in boids]
    kdtree = KDTree(boids_positions)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 監控點擊事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 若是點擊btn1(控制OBSTACLES)
            if btn1.collidepoint(event.pos):
                # 點擊後由 True->False or False->True
                btn1_c = not btn1_c
            # 若是點擊btn2(控制PREDATORS)
            if btn2.collidepoint(event.pos):
                # 點擊後由 True->False or False->True
                btn2_c = not btn2_c
                if btn2_c:
                    predator = Predator()

    screen.fill(BLACK, (0, 0, WIDTH, HEIGHT-30))
    screen.fill(WHITE, (0, HEIGHT-30, WIDTH, 30))

    # Draw button
    pygame.draw.rect(screen, DARK_BLUE, btn1)
    pygame.draw.rect(screen, DARK_BLUE, btn2)
    # OBSTACLES
    # 當True, 則設置障礙物
    if btn1_c:
        screen.blit(btn1_text_c, btn1)
        obstacles = [(WIDTH / 3, HEIGHT / 3, 10), (WIDTH * 2 / 3, HEIGHT * 2 / 3, 10)]
    # 當False, 則不設置障礙物
    else:
        screen.blit(btn1_text, btn1)
        obstacles = []
    # PREDATOR
    # 當True, 則設置獵食者
    if btn2_c:
        screen.blit(btn2_text_c, btn2)
        predator.update_predator(kdtree, boids, obstacles)
        predator.draw()
        # boids
        for boid in boids:
            boid.update_boid(kdtree, boids, obstacles, predator)
            boid.draw()
    # 當False, 則不設置獵食者
    else:
        screen.blit(btn2_text, btn2)
        # boids
        for boid in boids:
            boid.update_boid(kdtree, boids, obstacles, None)
            boid.draw()

    # 設定障礙物
    for obstacle in obstacles:
        pygame.draw.circle(screen, PINK, (obstacle[0], obstacle[1]), obstacle[2])

    pygame.display.update()
    clock.tick(FPS)

# 關閉 Pygame
pygame.quit()
