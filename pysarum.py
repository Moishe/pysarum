import matplotlib.pyplot as plt
import numpy as np

WIDTH = 1024
HEIGHT = 1024

LOOK_DISTANCE = 15
RANDOM_WANDER = np.pi / 3
MAX_FOOD = 32

values = np.empty((WIDTH, HEIGHT))
food = np.full((WIDTH, HEIGHT), MAX_FOOD)

class Director():
    def __init__(self, max_actor_count=1024, initial_actor_count=1):
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
        for (idx, actor) in enumerate(self.actors):
            if isinstance(actor, Actor):
                if not actor.step():
                    self.actors[idx] = self.next_free
                    self.next_free = idx
                elif actor.should_spawn():
                    self.add_actor(Actor(actor))


class Actor():
    def __init__(self, parent=None):
        if (parent):
            self.x = parent.x
            self.y = parent.y
            self.direction = parent.direction + np.random.random_sample() - 0.5
        else:
            self.x = np.round(WIDTH / 2)
            self.y = np.round(HEIGHT / 2)
            self.direction = np.random.random_sample() * np.pi * 2

    def should_spawn(self):
        return np.random.random_sample() < 0.01

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
                    v = values[lx, ly]
                    if v > best_v:
                        v = best_v
                        best_d = ld

        return best_d

    def deposit(self):
        amt = 1
        rx = round(self.x)
        ry = round(self.y)
        for d in range(0, 3):
            for x in range(max(0, rx - d), min(WIDTH, rx + d + 1)):
                for y in range(max(0, ry - d), min(HEIGHT, ry + d + 1)):
                    values[x, y] += amt
            amt *= 0.5

        food[rx, ry] -= 1

    def step(self):
        self.direction = self.best_direction()
        self.deposit()
        self.x += np.cos(self.direction)
        self.y += np.sin(self.direction)
        self.direction += (np.random.random_sample() - 0.5) * RANDOM_WANDER

        if round(self.x) >= WIDTH:
            self.x = WIDTH / 2

        if round(self.y) >= HEIGHT:
            self.y = HEIGHT / 2

        return food[round(self.x), round(self.y)] > 0

def start():
    global WIDTH, HEIGHT

    director = Director()

    for g in range(0, 1024):
        director.step()

    fig, ax = plt.subplots()
    plt.axis('off')
    plt.contour(range(0, WIDTH), range(0, HEIGHT), values, levels=30, alpha = 0.8, linewidths = 0.1, colors='black')
    plt.savefig('myimage.svg', format='svg', dpi=1200)

if __name__ == '__main__':
    start()