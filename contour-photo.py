import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
from numpy import asarray
from matplotlib.pyplot import show
from scipy.ndimage import gaussian_filter
from scipy.special import expit

# load the image
image = Image.open('/Users/moishe/Desktop/flash_tree-23.jpg')
# convert image to numpy array
data = asarray(image)
print(data.shape)

WIDTH = data.shape[0]
HEIGHT = data.shape[1]

data = gaussian_filter(data, sigma=1)

fig = plt.gcf()
INCH_HEIGHT = 8
INCH_WIDTH = INCH_HEIGHT * (WIDTH / HEIGHT)
fig.set_size_inches(INCH_HEIGHT, INCH_WIDTH)
plt.axis('off')
data = np.rot90(data[:,:,0], 2)
plt.contour(range(0, HEIGHT), range(0, WIDTH), data, levels=8, alpha = 0.8, linewidths = 0.1, colors='black')
plt.savefig('contour-image.svg', format='svg', dpi=1200)
show()
