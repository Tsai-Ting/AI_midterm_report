# 可調整參數
SIZE = (100, 100)  # 地圖大小
ITERATIONS = 300  # 跑出幾幀畫面
SEED = 42  # 生成初始地圖用亂數
# Conway 本體
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import Image
fig, ax = plt.subplots()
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])


class Conway:
    alive_rule = np.zeros(9, np.uint8)
    alive_rule[[2, 3]] = 1
    dead_rule = np.zeros(9, np.uint8)
    dead_rule[3] = 1

    def __init__(self, size: tuple[int, int] = (20, 20), seed=None) -> None:
        if seed is None:
            seed = np.random.randint(0, 2**31)
        np.random.seed(seed)
        self.size = size
        self.canvas = np.random.randint(0, 2, size=size)
        self.kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ])

    def advance(self):
        convolution = convolve2d(self.canvas, self.kernel, mode="same").astype(int)
        self.canvas = np.where(
            self.canvas, Conway.alive_rule[convolution], Conway.dead_rule[convolution]
        )
        return self.canvas

    def animate(self, iterations=ITERATIONS):
        im = plt.imshow(self.canvas, cmap="viridis")

        def update(_):
            self.advance()
            im.set_array(self.canvas)
            return im

        anim = animation.FuncAnimation(fig, update, frames=iterations, interval=50)
        anim.save("conway.gif")


conway = Conway(size=SIZE, seed=SEED)
conway.animate()
Image("conway.gif")
