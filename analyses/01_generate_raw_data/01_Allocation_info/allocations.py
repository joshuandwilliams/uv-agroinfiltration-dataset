"""
Randomly allocates raw agroinfiltration TIF images to scorers.

Reads image_paths.csv (TIF file paths) and image_info.csv (estimated CDA counts
per image), shuffles images randomly, and saves the shuffled list as
randomised_info.csv. Scorer assignments (scorer1, scorer2, scorer3 columns) were
added to the output manually using the staggered allocation pattern described in
the dataset documentation.

Run once before annotation began for each dataset part. Set SET to the dataset
part number (1 or 2) to filter image_info.csv to the correct rows.

Inputs:  image_paths.csv, image_info.csv
Output:  randomised_info.csv
"""
import os

import pandas as pd

HERE = os.path.dirname(__file__)

SET = 1  # Dataset part to allocate (1 or 2)
N_SCORERS = {1: 8, 2: 9}[SET]

image_paths = pd.read_csv(os.path.join(HERE, "image_paths.csv"))
imginfo = pd.read_csv(os.path.join(HERE, "image_info.csv"))
imginfo = imginfo[imginfo['Set'] == SET]

shuffled_images = image_paths.sample(frac=1).reset_index()

# Target CDA count per scorer batch
cda_cutoff = sum(imginfo['CDA_Count_Image'] / N_SCORERS)


def retrieve_count(path):
    match_index = imginfo['Image'][imginfo['Image'] == os.path.basename(path)].index[0]
    return imginfo.loc[match_index, 'CDA_Count_Image']


for index, row in shuffled_images.iterrows():
    shuffled_images.loc[index, 'count'] = retrieve_count(shuffled_images.loc[index, 'path'])
    shuffled_images.loc[index, 'basename'] = os.path.basename(shuffled_images.loc[index, 'path'])

shuffled_images = shuffled_images.drop_duplicates(subset=['basename'], keep='first')

# Print running CDA count at each batch boundary for verification
cda_count = 0
for index, row in shuffled_images.iterrows():
    cda_count += shuffled_images.loc[index, 'count']
    if cda_count > cda_cutoff:
        print(f"Batch boundary at image {index}: cumulative CDAs = {cda_count:.0f}")
        cda_count = 0
print(f"Final batch: {cda_count:.0f} CDAs (total: {sum(shuffled_images['count']):.0f})")

shuffled_images.to_csv(os.path.join(HERE, "randomised_info.csv"))
