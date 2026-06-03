"""
Distributes raw agroinfiltration TIF images to scorer folders for annotation.

Reads randomised_info.csv (scorer assignments per image) and image_info.csv
(orientation values), then copies each image to the three assigned scorer folders
on the lab shared drive, applying rotation correction where needed before copying.

Run once before annotation began for each dataset part.

Inputs:  randomised_info.csv, image_info.csv
Output:  TIF files copied to SCORING_DIR/<scorer>/ folders
"""
import os
import subprocess

import pandas as pd
from PIL import Image

BASE_DIR = "/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams"

SCORING_DIRS = {
    1: os.path.join(BASE_DIR, "Scoring_5May"),
    2: os.path.join(BASE_DIR, "Scoring_20Oct"),
}

SET = 1  # Dataset part to distribute (1 or 2)
SCORING_DIR = SCORING_DIRS[SET]

data = pd.read_csv("analyses/01_generate_raw_data/01_allocation_info/randomised_info.csv")
data = data[data['Set'] == SET]
image_info = pd.read_csv("analyses/01_generate_raw_data/01_allocation_info/image_info.csv")

for index, row in data.iterrows():
    print(f"Progress: {index + 1} / {len(data)}")
    img_path = data.loc[index, 'Path']

    out_dest_1 = os.path.join(SCORING_DIR, data.loc[index, 'scorer1'])
    out_dest_2 = os.path.join(SCORING_DIR, data.loc[index, 'scorer2'])
    out_dest_3 = os.path.join(SCORING_DIR, data.loc[index, 'scorer3'])

    orientation = image_info['Orientation'][image_info['Image'] == os.path.basename(img_path)].values[0]

    if orientation != 0:
        print(f"  Rotating {os.path.basename(img_path)} by {orientation * 90}° clockwise")
        img = Image.open(img_path)
        img = img.rotate(-(orientation * 90), expand=True)
        rotated_path = os.path.basename(img_path)
        img.save(rotated_path, "TIFF")
        subprocess.run(["cp", rotated_path, out_dest_1])
        subprocess.run(["cp", rotated_path, out_dest_2])
        subprocess.run(["cp", rotated_path, out_dest_3])
    else:
        subprocess.run(["cp", img_path, out_dest_1])
        subprocess.run(["cp", img_path, out_dest_2])
        subprocess.run(["cp", img_path, out_dest_3])
