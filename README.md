# Image colour count

This repository contains a python script to count the occurrence of every colour in an image. The colour count is either the count of each colour present in the shape, or the count of the occurrences of the specified reference colours. 

Instructions for use:

1. Download the file ‘colour_count.py’.

2. Set the folder containing the images for which the colour count should be computed. Defaults to the directory the script is executing.

3. Set the folder to save the computation results. Defaults to the directory the script is executing. 

4. 3. (Optional) Set the reference colours, if needed. Other colours different from the specified reference colours will be counted as the most similar reference colour. If no reference colour is specified, each colour is counted as is.  
Reference colours should be specified as `"<colour_name>": (R, G, B)`, e.g.:
```python
REFERENCE_colours = {
    "background": (255,255,255),
    ...
}
```

Execute the script.

The script will read the images contained in the folder specified in `input_folder` and for each of them it will produce in `output_folder` a JSON file containing the absolute and relative frequency for each colour. It will also generate an hystogram for each image with the colours' occurrences. If a threshold is defined, only the hystograms related to the colours whose relative frequency is above it will be displayed.
