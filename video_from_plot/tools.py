# generate_video requires ffmpeg

import subprocess
from glob import glob
from pathlib import Path
import matplotlib.pyplot as plt

def generate_video(plot_function,t_max,directory='figs',filename='out',
                   framerate=30,dpi=300,rm_images=True,transparent=False):
    
    if t_max >= 1e5:
        raise ValueError(f"Do you really want to save {t_max} images? Try smaller.")
    
    # create figure dir if doesn't exist
    Path(directory).mkdir(exist_ok=True)

    # generate images from plot_function
    for t in range(t_max):
        plot_function(t)
        tmp = str(plot_function.__hash__())  # tmp identifier so you don't clobber other files
        plt.savefig(f"{Path(directory,tmp)}_{t:05d}.png", dpi=dpi, transparent=transparent)
        if t>0: plt.close()
    
    # call ffmpeg, removing temporary images afterwards (true by default)
    filename_=f"{Path(directory,filename)}.mp4"
    cmdstring = ('ffmpeg', '-loglevel', 'warning', '-y', '-r', f'{framerate}',
        '-pattern_type', 'glob', '-i', f'{Path(directory,tmp)}*.png',  # input images are globbed pngs
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',  # video codec and pixel format
        '-vf', 'crop=trunc(iw/2)*2:trunc(ih/2)*2',
        filename_)
    subprocess.call(cmdstring)
    print(f"created {filename_}")
    if rm_images:
        subprocess.call(['rm']+glob(f"{Path(directory,tmp)}*.png"))
