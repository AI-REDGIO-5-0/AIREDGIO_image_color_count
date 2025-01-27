# %% [markdown]
# # AI REDGIO 5.0 - Colours analysis 

# %% [markdown]
# Extract colours count from an image.  
# The colour count is either the count of each colour present in the shape, or the count of the occurrences of the specified reference colours. 

# %% [markdown]
# ## Parameters settings

# %% [markdown]
# 1. Set the folder containing the images for which the colour count should be computed. Defaults to the directory the script is executing. 

# %%
input_folder = ''

# %% [markdown]
# 2. Set the folder to save the computation results. Defaults to the directory the script is executing. 

# %%
output_folder = ''

# %% [markdown]
# 3. (Optional) Set the reference colours, if needed. Other colours different from the specified reference colours will be counted as the most similar reference colour. If no reference colour is specified, each colour is counted as is.  
# Reference colours should be specified as `"<colour_name>": (R, G, B)`, e.g.:
# ```python
# REFERENCE_colours = {
#     "background": (255,255,255),
#     ...
# }
# ```

# %%
REFERENCE_colours = {}

# %% [markdown]
# 4. (Optional) Define the cut-off percentage to display the colours histogram (from 0 to 1).

# %%
treshold_plot = 0.01

# %% [markdown]
# ## Script execution

# %%
from PIL import Image
from collections import defaultdict
import math
import os
import json
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
import numpy as np

# %% [markdown]
# Compute "similarity" between colours by means of their distance

# %%
def euclidean_distance(colour1: tuple[float, ...], colour2: tuple[float, ...]) -> float:
    """
    Calculates the Euclidean distance between two colours in RGB space.

    Args:
        colour1 (tuple): The first colour (R, G, B).
        colour2 (tuple): The second colour (R, G, B).

    Returns:
        float: The Euclidean distance.
    """
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(colour1, colour2)))
    # return np.linalg.norm(np.array(colour1) - np.array(colour2))

# %%
def closest_reference_colour(colour: tuple[float, ...], references: dict[str, tuple[float, ...]]):
    """
    Finds the closest reference colour for the given colour.

    Args:
        colour (tuple): The colour (R, G, B).

    Returns:
        str: The key of the closest reference colour.
    """
    return min(references, key=lambda ref: euclidean_distance(colour, references[ref]))

# %% [markdown]
# Count all the colours' occurrences

# %%
def colours(image, references: dict = dict(), ignore: set = set()) -> dict[str, dict[str, float]]:
    aggregated_data = {}
    try:
        # Get all pixels as a flat list
        pixels = list(image.convert("RGB").getdata())
        unique_elements, counts = np.unique(pixels, return_counts=True, axis=0)
        pixels = zip(unique_elements, counts)
        # Process the image
        if ignore:
            pixels = [p for p in pixels if p[0] not in ignore]
        if references:
            def closest_colour(c: tuple[float, ...]):
                return closest_reference_colour(c, references)
            # pixels = map(
            #     closest_colour,
            #     tqdm(pixels, desc='Finding similar colours...')
            # )
            pixels = [(closest_colour(c[0]), c[1]) for c in tqdm(pixels, desc='Finding similar colours...')]
        # unique_elements, counts = np.unique(pixels, return_counts=True, axis=0)
        # data = dict(zip(unique_elements, counts))
        # data = dict(Counter(pixels))
        # Initialize a defaultdict
        accumulator = defaultdict(int)
        # Accumulate counts
        for a, b in pixels:
            accumulator[f'{a[0]} {a[1]} {a[2]}'] += int(b)
        data = dict(accumulator)
        total = sum(data.values())
        aggregated_data = {
            k: {
                'count': v,
                'percentage': v/total
            }
            for k, v in data.items()
        }
        for k, v in aggregated_data.items():
            v['rgb'] = *map(int, references.get(k, k).split(' ')),
    except FileNotFoundError:
        print("Error: File not found. Please provide a valid image path.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        return aggregated_data
        

# %% [markdown]
# Create a histogram with the colours' occurrences

# %%
def plot(counts, filepath: str, threshold: float = 0):

    """
    threshold: treshold value on the percentage of occurrences
    """

    data = [(str(k), v['rgb'], v['count']) for k, v in counts.items() if v['percentage'] >= threshold]
    data = sorted(data, key=lambda c: c[2], reverse=True)
 
    names, colours, occurrences = zip(*data)
 
    # Normalize RGB values to the range [0, 1]
    colours_normalized = [(r / 255, g / 255, b / 255) for r, g, b in colours]
 
    plt.bar(names, occurrences, colour=colours_normalized, edgecolour = 'black')

    plt.xlabel('colour')
    plt.ylabel('Occurrences')
    plt.title('RGB Histogram')
 
    # Save the plot 
    plt.savefig(filepath)
    plt.close()

# %% [markdown]
# Loop over the files in the specified folder

# %%
input_folder = input_folder if input_folder else '.'
filenames = os.listdir(input_folder)
last_folder_name = os.path.basename(os.path.normpath(input_folder))
last_folder_name = last_folder_name if last_folder_name != '.' else ''

#creation of a folder with the name of the part in which save the extracted histograms
output_folder = output_folder if output_folder else '.'
output_folder_path_file = f'{output_folder}/{last_folder_name}_colour_analysis'
os.makedirs(output_folder_path_file, exist_ok=True)

# %%
progress = tqdm(filenames, desc='Reading files...')
for f in progress:
    try:
        filepath = os.path.join(input_folder, f)
        print(f'Reading file {f}... ', end='')
        with Image.open(filepath) as img:
            # img.verify()
            print()
            counts = colours(img, REFERENCE_colours)
        counts_filename, _ = os.path.splitext(f)
        counts_filepath = os.path.join(output_folder_path_file, f'{counts_filename}.json')
        with open(counts_filepath, 'w') as out_file:
            json.dump({str(k): v for k, v in counts.items()}, out_file, indent=4, default=int)
        histogram_filepath = os.path.join(output_folder_path_file, f'{counts_filename}_histogram.png')
        plot(counts, histogram_filepath, treshold_plot)
    except (IOError, SyntaxError):
        print(f'Not an image')


