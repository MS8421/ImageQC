# Image Quality Control

### <span style="color:grey">Python script that calculates image quality metrics of *.tif* images in a directory.</span>
* Only works with **.tif** files
* Takes directory path as an input when run, or the path can be specified in **command line** as: **
## QC metrics:
* <span style="color:green">**Signal noise ratio**</span> is calculated as a float
* <span style="color:green">**Blurriness**</span> is calculated as a float between 0 and 1
* Both metrics are saved alongside the name of their corresponding image to a **.csv** file for each directory.

## Useage example:
`python  main.py  /path/to/directory  /multiple/paths/also/work`

## Requirements:
`
imagecodecs
numpy
scikit-image
`