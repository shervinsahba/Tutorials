# generate_video requires ffmpeg

import os
import glob
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt

def generate_video(plot_function,t_max,directory,framerate=20,dpi=300,
                   filename='out',rm_images=True,transparent=False):
    # generate images from plot_function
    if t_max >= 1e5:
        raise ValueError("t_max too large! Choose a smaller time index.")

    Path(directory).mkdir(exist_ok=True)
    for t in range(t_max):
        plot_function(t)
        plt.savefig(directory + "/%05d.png" % t, dpi=dpi, transparent=transparent)
        if t>0: plt.close()

    # record current directory. make figure directory if doesn't exist. cd into it.
    previous_directory = os.getcwd()
    os.makedirs(directory, exist_ok=True)
    os.chdir(directory)

    # create video via ffmpeg, removing intermediate images after if wanted (true by default)
    # then return to previous dir
    try:
        filename_=f"{filename}.mp4"
        subprocess.call(f'ffmpeg -y -loglevel warning -framerate {framerate} -pattern_type glob -i *.png -c:v libx264 -pix_fmt yuv420p -vf crop=trunc(iw/2)*2:trunc(ih/2)*2 {filename_}'.split(' '))
        if rm_images: 
            subprocess.call(['rm']+glob.glob("*.png"))
        print(f"created {filename_}")
    finally:
        os.chdir(previous_directory)
