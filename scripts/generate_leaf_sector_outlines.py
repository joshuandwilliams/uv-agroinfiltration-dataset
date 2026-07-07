"""Generate leaf sector-outline CSVs used by analyses/08_leaf_positions/leaf_positions.qmd.

Segments benth_leaf.jpeg (in this same directory) into N radial sectors for
N=5, 6, and 8, and writes the polygon vertex coordinates for each to
analyses/08_leaf_positions/leaf_sector_csv_{N}.csv.

Run this only if those CSVs are missing or the reference leaf image changes.
"""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Polygon

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parents[0] / "analyses" / "08_leaf_positions"

# 1. Create leaf outline

image = cv2.imread(str(SCRIPT_DIR / "benth_leaf.jpeg"), cv2.IMREAD_GRAYSCALE)

# Generate a mask, and from the mask find contours
mask = cv2.inRange(image, 85, 255)
contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contour = max(contours, key=cv2.contourArea)  # Largest contour

coords = contour.squeeze()  # Extract coordinates

if not np.array_equal(coords[0], coords[-1]):  # If gap between start and end
    coords = np.vstack([coords, coords[0]])  # Close it

coords[:, 1] = image.shape[0] - coords[:, 1]  # Invert Y

centroid = np.mean(coords, axis=0)
leaf_polygon = Polygon(coords)

# Sanity-check plot of the extracted contour and centroid
plt.figure(figsize=(10, 10))
plt.plot(coords[:, 0], coords[:, 1], "b-", label="Leaf Contour")
plt.plot(centroid[0], centroid[1], "ro", label="Centroid")
plt.fill(coords[:, 0], coords[:, 1], alpha=0.3)
plt.gca().invert_yaxis()
plt.show()


# 2. Segment leaf outline


def generate_sector_angles(num_sectors):
    sector_angles = []
    if num_sectors % 2 == 0:
        # If num_sectors is even, all sector angles are the same
        angle = 360 / num_sectors
        sector_angles = [angle] * num_sectors
    else:
        # If num_sectors is odd
        half_sectors = num_sectors // 2
        first_half_sectors = half_sectors + 1  # First half gets an extra sector
        second_half_sectors = half_sectors

        angle_first_half = 180 / first_half_sectors
        angle_second_half = 180 / second_half_sectors if second_half_sectors != 0 else 0

        # First half sectors angles
        sector_angles.extend([angle_first_half] * first_half_sectors)
        # Second half sectors angles
        sector_angles.extend([angle_second_half] * second_half_sectors)

    return sector_angles


def segments_csv(leaf_polygon, num_sectors):
    sector_angles = generate_sector_angles(num_sectors)
    print(sector_angles)

    # Generate sector coordinates
    sectors = []
    angle_accumulated = 0
    for i in range(num_sectors):
        angle_start = np.deg2rad(
            angle_accumulated + 90
        )  # 90 makes first line point north of centroid
        angle_accumulated += sector_angles[i]
        angle_end = np.deg2rad(angle_accumulated + 90)
        # Huge triangle between the centroid, the start angle, and the end angle,
        # then confined to the limits of the leaf polygon.
        sector = Polygon(
            [
                centroid,
                centroid + 10000 * np.array([np.cos(angle_start), np.sin(angle_start)]),
                centroid + 10000 * np.array([np.cos(angle_end), np.sin(angle_end)]),
                centroid,
            ]
        )
        sectors.append(sector.intersection(leaf_polygon))

    # Convert sectors to DataFrame
    sector_coords = []
    for i, sector in enumerate(sectors):
        if not sector.is_empty:
            # Arrays of x and y values at each vertex of the sector shape
            x, y = sector.exterior.xy
            sector_coords.extend(
                # One tuple per vertex, containing x, y, and sector index
                [(xi, yi, i + 1) for xi, yi in zip(x, y, strict=False)]
            )
    sector_df = pd.DataFrame(sector_coords, columns=["x", "y", "sector"])

    # Save to CSV
    sector_df.to_csv(OUTPUT_DIR / f"leaf_sector_csv_{num_sectors}.csv")

    # Plot sectors to verify
    plt.figure(figsize=(6, 6))
    colours = plt.cm.viridis(np.linspace(0, 1, num_sectors))
    for i, sector in enumerate(sectors):
        if not sector.is_empty:
            x, y = sector.exterior.xy
            plt.fill(x, y, color=colours[i], label=f"Sector {i+1}")
    plt.show()


if __name__ == "__main__":
    segments_csv(leaf_polygon, 5)
    segments_csv(leaf_polygon, 6)
    segments_csv(leaf_polygon, 8)
