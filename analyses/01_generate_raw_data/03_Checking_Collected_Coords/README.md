# 03_checking_collected_coords

Manual quality check of the bounding box annotations collected by CDAScorer.
Only coordinate annotations were corrected — scores were never modified.

Score-based filtering (removing CDAs with insufficient or disagreeing annotations)
is handled programmatically by `clean_scores()` in the next step
(`04_median_and_centre_coords`).

## Manual checking process

Each CDA annotation was reviewed one by one using the viewer scripts in this
folder. For every CDA, the bounding boxes drawn by each scorer were inspected
against the raw agroinfiltration image to verify they were correctly placed.

At least 100–200 corrections were made across both dataset parts:

- **Coordinate corrections** — bounding boxes not covering the correct CDA were
  corrected to the right `Row`, `Col`, `Pos` reference, or removed entirely.
  Criteria for removal: box not on a CDA, only partially covering a CDA, or
  spanning multiple CDAs.
- **Duplicate removal** — where two annotations were collected by the same scorer
  for the same CDA, only the first-appearing annotation in the table was kept.

## Files

### `combined_cda_data_checked_1.csv` / `combined_cda_data_checked_2.csv`
Manually reviewed versions of `combined_cda_data_1.csv` / `combined_cda_data_2.csv`
from the previous step. These are the inputs to `04_median_and_centre_coords`.

| File | Rows |
|------|------|
| `combined_cda_data_checked_1.csv` | 2,811 |
| `combined_cda_data_checked_2.csv` | 3,997 |

### `view_each_cda.qmd`
Tkinter viewer that steps through each CDA one at a time, displaying all bounding
boxes and scores for that CDA overlaid on the raw image. Left/right arrow keys
to navigate. Requires connection to the lab network drive.

### `view_each_raw_img.qmd`
Tkinter viewer that displays all CDA annotations for an entire raw agroinfiltration
image at once. Press space to save the current canvas as a JPG (used to generate
`dsc_0103_example_annotations.jpg`). Requires connection to the lab network drive.

### `dsc_0103_example_annotations.jpg`
Example output showing all annotations overlaid on a raw agroinfiltration image,
illustrating the checking process.
