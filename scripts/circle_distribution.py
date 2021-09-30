import numpy as np
import matplotlib.pyplot as plt



noise_x = 2
noise_y = 2
radius = 5
alpha = np.random.uniform(0, 2*np.pi, 100)
noise = np.random.multivariate_normal([0,0], np.array([[noise_x, 0], [0, noise_y]]),100)
X = radius*np.array([np.cos(alpha),np.sin(alpha)]).T + noise + np.array([100, 200]).T
plt.scatter([x for x,_ in X], [y for _,y in X])
plt.show()