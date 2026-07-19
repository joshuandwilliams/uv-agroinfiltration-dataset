# 03_checking_collected_coords

Manual quality check of the bounding box annotations collected by CDAScorer.
Only coordinate annotations were corrected — scores were never modified.

Score-based filtering (removing CDAs with insufficient or disagreeing annotations)
is handled programmatically by `clean_scores()` in the next step
(`04_median_and_centre_coords`).

## Manual checking process

Each CDA annotation was reviewed one by one using `annotation_viewer.qmd` in
`'cda'` mode, which steps through a single CDA at a time. This mode was used for
both dataset parts. For every CDA, the bounding boxes drawn by each scorer were
inspected against the source agroinfiltration image to verify they were correctly
placed. (The viewer's `'raw'` mode, which shows a whole image at once, was only
used to test functionality and not for the checking itself.)

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

### `annotation_viewer.qmd`
Interactive Tkinter viewer (wraps `view_annotations()` in `src/annotation_viewer.py`).
Left/right arrow keys navigate; spacebar saves the current view as a JPG. Two modes:
- `'cda'` — steps through one CDA at a time. Used for the manual checking above.
- `'raw'` — displays all CDA annotations for an entire source image at once. Only
  used to test functionality.

Requires connection to the lab network drive.

### `save_annotation_images.qmd`
Headless batch export (wraps `save_all_annotation_images()`). Generates a JPEG for
every source agroinfiltration image in both checked datasets, with all bounding
boxes overlaid, written to `data/annotations/`. Requires connection to the lab
network drive.

### `checking_summary.qmd` / `checking_summary.html`
Quantifies the manual checking by comparing coordinates before (step 02) and after
checking, reporting how many CDAs were added/removed and how many annotations had
their coordinates changed.
