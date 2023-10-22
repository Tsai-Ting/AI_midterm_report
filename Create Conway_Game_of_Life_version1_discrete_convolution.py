# 可調整參數
SIZE = (100, 100)  # 地圖大小
ITERATIONS = 100  # 跑出幾幀畫面
SEED = 42  # 生成初始地圖用亂數
# Conway本體
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import Image
fig, ax = plt.subplots()
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])

def linear_interpolation(cv: np.ndarray, conv: np.ndarray):
    mask = np.where(conv < 1)
    cv[mask] = 0

    mask = np.where((1 <= conv) & (conv < 2))
    cv[mask] = cv[mask] * (2 - conv[mask])

    mask = np.where((2 <= conv) & (conv < 3))
    cv[mask] = 1*(3-conv[mask]) + cv[mask]*(conv[mask]-2),

    mask = np.where((3 <= conv) & (conv < 4))
    cv[mask] = 1 * (conv[mask] - 3)

    mask = np.where(conv >= 4)
    cv[mask] = 0

    return cv

class LinearConway:
    def __init__(self, size: tuple[int, int] = (20, 20), seed=None) -> None:
        if seed is None:
            seed = np.random.randint(0, 2**31)
        rng = np.random.default_rng(seed)
        self.size = size
        self.canvas = rng.random(size)
        self.kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ]).astype(np.float64)

    def advance(self):
        convolution = convolve2d(self.canvas, self.kernel, mode="same")
        self.canvas = linear_interpolation(self.canvas, convolution)
        return self.canvas

    def animate(self, iterations=ITERATIONS):
        im = plt.imshow(self.canvas, cmap="viridis")

        def update(_):
            self.advance()
            im.set_array(self.canvas)
            return im

        anim = animation.FuncAnimation(fig, update, frames=iterations, interval=75)
        anim.save("gol.gif")


conway = LinearConway(size=SIZE, seed=SEED)
conway.animate()
Image("gol.gif")
