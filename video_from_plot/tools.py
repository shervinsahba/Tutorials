# generate_video requires ffmpeg!

import subprocess
from glob import glob
from pathlib import Path
import matplotlib.pyplot as plt
from tqdm import tqdm
import gc
import matplotlib

def call_ffmpeg(filename,directory,image_name_prefix,framerate=30):
    """Generates a video from images using ffmpeg.

    Args:
        filename: output video file basename. Example: "video" if you want video.mp4.
        directory: directory to output video as well as directory to find images
        image_name_prefix: prefix of images. Example: "img_" represents all images img_00000.png through img_99999.png.
        framerate: framerate to pass to ffmpeg.
    """
    filename=f"{Path(directory,filename)}.mp4"
    cmdstring = ('ffmpeg', '-loglevel', 'warning', '-y', '-r', f'{framerate}',
        '-pattern_type', 'glob', '-i', f'{Path(directory,image_name_prefix)}*.png',  # input images are globbed pngs
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',  # video codec and pixel format
        '-vf', 'crop=trunc(iw/2)*2:trunc(ih/2)*2', # truncate to an even number of pixels (needed for some codecs)
        filename)  # save as filename
    try:
        subprocess.call(cmdstring)
        print(f"Created {filename}")
    except Exception as e:
        print("Video generation failed. Check ffmpeg?", e)


def generate_video(plot_function,t_max,t_start=0,directory='figs',filename='video',
                   framerate=30,dpi=300,transparent=False,rm_images=True):
    """Generates a video from a matplotlib function handle. 
    Creates t_max-t_start many temporary images and passes them to ffmpeg for video creation.

    Args:
        plot_function (matplotlib function): matplotlib function handle
        t_max (int): Last index to plot.
        t_start (int, optional): Beginning index to plot. Defaults to 0.
        directory (str, optional): Relative working directory. Defaults to 'figs'.
        filename (str, optional): Output filename. Defaults to 'video'.
        framerate (int, optional): Video framerate. Defaults to 30.
        dpi (int, optional): Image quality DPI. Defaults to 300.
        transparent (bool, optional): Image transparency. Defaults to False.
        rm_images (bool, optional): Removes all temproary images. Defaults to True.

    Raises:
        ValueError: As a safeguard, the function won't let you generate more than 1e5 images as written.
    """
    if t_max - t_start >= 1e5:
        raise ValueError(f"Do you really want to save {t_max - t_start} images? Try smaller.")

    print(f"Generating video with {t_max - t_start} frames")

    Path(directory).mkdir(exist_ok=True)  # create figure dir if doesn't exist
    image_name_prefix = str(plot_function.__hash__())   # tmp identifier so you don't clobber other files
    
    # TODO note that matplotlib may have memory leaks on looping figures. See for example:
    # https://github.com/matplotlib/matplotlib/issues/20300
    # https://github.com/matplotlib/matplotlib/issues/25406
    print("Reseting matplotlib font family to default and switching to agg backend to avoid a memory leak.")
    plt.rcParams.update({"font.family": "serif"})
    matplotlib.use('agg')  # switch to a non-interactive backend

    # generate temporary images from plot_function
    for t in tqdm(range(t_start,t_max)):
        plot_function(t)
        plt.gcf().savefig(f"{Path(directory,image_name_prefix)}_{t:05d}.png", dpi=dpi, transparent=transparent)
        plt.close()     # close figure to save memory
        gc.collect()    # garbage collect
 
    call_ffmpeg(filename,directory,image_name_prefix)

    if rm_images:  # remove temporary images
        subprocess.call(['rm']+glob(f"{Path(directory,image_name_prefix)}*.png"))