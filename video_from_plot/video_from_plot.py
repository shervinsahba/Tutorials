import numpy as np
import matplotlib.pyplot as plt
from tools import generate_video

x = np.linspace(0, 2*np.pi, num=100)
data = np.array([np.sin(x-t) for t in range(1000)])

def plot_simple_1d(x,y):
    fig,ax = plt.subplots(1,1,figsize=(4,2))
    ax.plot(x,y)
    ax.set_xlim(x[0],x[-1])

generate_video(lambda t: plot_simple_1d(x, data[t,:]), 100, 'figs')
