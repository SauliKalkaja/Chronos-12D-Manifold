import imageio.v2 as imageio
import glob
import os

# 1. Locate the frames from your 6D sweep
frame_folder = "hurricane_katrina"
# Grab all pngs and sort them so they play in the correct chronological order
filenames = sorted(glob.glob(os.path.join(frame_folder, "frame_*.png")))

if not filenames:
    print(f"No frames found in '{frame_folder}'! Make sure you ran the analysis script first.")
else:
    print(f"Found {len(filenames)} frames. Stitching the 6D Manifold together...")
    
    # 2. Read the images into a list
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
        
    # 3. Save as an animated GIF
    output_gif = "Hurricane_Cathrine_6D_Animation.gif"
    
    # 'duration' is seconds per frame. 
    # 0.2 seconds = 5 frames per second. Adjust this to make it faster or slower!
    imageio.mimsave(output_gif, images, duration=0.2)
    
    print(f"Success! Your animation is ready: {output_gif}")