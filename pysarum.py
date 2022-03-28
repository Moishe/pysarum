import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
from matplotlib.pyplot import show
from scipy.ndimage import gaussian_filter

WIDTH = 1024
HEIGHT = 1024
MAX_FOOD_VALUE = 64
SPAWN_DENOMINATOR = 32
MAX_VALUE = 64

LOAD_FROM_FILE = False

SEED_LOC_F = lambda: (WIDTH / 2, HEIGHT / 2)

LOOK_DISTANCE = 15
RANDOM_WANDER = np.pi / 3
MAX_FOOD = 16

food = None
values = None

class Director():
    def __init__(self, max_actor_count=4096, initial_actor_count=1):
        self.actors = [] # if int, it's the next_free; otherwise an actor
        for i in range(0, max_actor_count):
            self.actors.append(i - 1)
        self.next_free = i - 1

        for i in range(0, initial_actor_count):
            self.add_actor(Actor())

    def add_actor(self, actor):
        if self.next_free != -1:
            idx = self.next_free
            self.next_free = self.actors[self.next_free]
            self.actors[idx] = actor
            return True
        else:
            return False

    def step(self):
        global values
        for (idx, actor) in enumerate(self.actors):
            if isinstance(actor, Actor):
                if not actor.step():
                    self.actors[idx] = self.next_free
                    self.next_free = idx
                elif actor.should_spawn():
                    self.add_actor(Actor(actor))
        blurred_values = gaussian_filter(values, sigma=0.1)
        values = blurred_values

class Actor():
    def __init__(self, parent=None):
        if (parent):
            self.x = parent.x
            self.y = parent.y
            self.direction = parent.direction + np.random.random_sample() - 0.5
        else:
            (x, y) = SEED_LOC_F()
            self.x = x
            self.y = y
            self.direction = np.random.random_sample() * np.pi * 2

    def should_spawn(self):
        return np.random.random_sample() * MAX_FOOD_VALUE * SPAWN_DENOMINATOR < food[int(np.round(self.x)), int(np.round(self.y))]

    def best_direction(self):
        best_v = 0
        best_d = self.direction

        # to-do: randomize the order of looking
        slices = list(range(0, 3))
        np.random.shuffle(slices)

        for d in slices:
            sides = [-1, 1]
            np.random.shuffle(sides)

            for lr in sides:
                ld = self.direction + (d / 3 * np.pi / 3 * lr)
                lx = round(np.cos(ld) * LOOK_DISTANCE + self.x)
                ly = round(np.sin(ld) * LOOK_DISTANCE + self.y)
                if lx > 0 and ly > 0 and lx < WIDTH and ly < HEIGHT:
                    v = values[lx, ly] + food[lx, ly]
                    if v > best_v:
                        v = best_v
                        best_d = ld

        return best_d

    def deposit(self):
        amt = 1
        rx = round(self.x)
        ry = round(self.y)

        values[rx, ry] = min(values[rx, ry] + 1, MAX_VALUE)
        food[rx, ry] -= 1

    def step(self):
        self.direction = self.best_direction()
        self.deposit()
        self.x += np.cos(self.direction)
        self.y += np.sin(self.direction)
        self.direction += (np.random.random_sample() - 0.5) * RANDOM_WANDER

        if round(self.x) >= WIDTH or round(self.y) >= HEIGHT:
            (x, y) = SEED_LOC_F()
            self.x = x
            self.y = y

        return food[round(self.x), round(self.y)] > 0

sorted_value_map = []
cur_brightest_value_idx = 0
def cur_brightest():
    global cur_brightest_value_idx, sorted_value_map
    value = sorted_value_map[cur_brightest_value_idx][1]
    cur_brightest_value_idx = (cur_brightest_value_idx + 9) % len(sorted_value_map)
    return value

sigmoid = lambda x: 1/(1 + np.exp(-(x / 255.0 * 20 - 10)))

def start():
    global WIDTH, HEIGHT, SEED_LOC_F, values, food, sorted_value_map

    np.random.seed(1)

    if LOAD_FROM_FILE:
        values = np.load('processed.npy')
        WIDTH = values.shape[0]
        HEIGHT = values.shape[1]
    else:
        im = Image.open('/Users/moishe/Desktop/ghost-small.jpg')
        rgb_im = im.convert('RGB')

        WIDTH = im.width
        HEIGHT = im.height

        values = np.empty((WIDTH, HEIGHT))
        food = np.full((WIDTH, HEIGHT), MAX_FOOD)

        value_map = {}
        for x in range(0, WIDTH):
            for y in range(0, HEIGHT):
                value = rgb_im.getpixel((x,y))[0]
                food[x,y] = sigmoid(value) * MAX_FOOD_VALUE

                if value not in value_map:
                    value_map[value] = (x,y)
                elif np.random.random_sample() < 0.5:
                    value_map[value] = (x,y)

        sorted_value_map = list(reversed(sorted(value_map.items(), key=lambda x: x[0])))
        #SEED_LOC_F = cur_brightest
        SEED_LOC_F = lambda: (np.floor(np.random.random_sample() * WIDTH),
                              np.floor(np.random.random_sample() * HEIGHT))


        director = Director(2048, 256)

        for g in range(0, 2048):
            print(g)
            director.step()

        np.save('processed', values)
    # blur the whole image
    #blurred_values = gaussian_filter(values, sigma=2)
    blurred_values = values

    fig = plt.gcf()
    fig.set_size_inches(10, 8)
    plt.axis('off')
    plt.contour(range(0, HEIGHT), range(0, WIDTH), blurred_values, levels=3, alpha = 0.8, linewidths = 0.1, colors='black')
    plt.savefig('myimage-2.svg', format='svg', dpi=1200)
    show()

if __name__ == '__main__':
    start()