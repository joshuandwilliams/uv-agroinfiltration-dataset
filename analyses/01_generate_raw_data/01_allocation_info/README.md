# 01_allocation_info

Reference files used to set up the scoring workflow before annotation began, and
to verify the allocation in downstream analyses. There are two dataset parts
(Set 1: 8 scorers, 89 images; Set 2: 9 scorers, 123 images; 7 scorers common to both).

## Files

### `image_info.csv` — manually created
Manually recorded before annotation began for each dataset part. Contains one row
per raw agroinfiltration image with the following columns:

| Column          | Description                                                  |
|-----------------|--------------------------------------------------------------|
| Set             | Dataset part (1 or 2)                                        |
| Path            | Folder path within the experiment directory                  |
| Image           | TIF filename                                                 |
| CDA_Per_Leaf    | Estimated number of CDAs per leaf                            |
| CDA_Count_Image | Estimated total CDAs per image (used for allocation)         |
| Orientation     | Clockwise 90° rotations needed to correct image orientation  |

Used by: `scripts/allocations.py`, `scripts/movefiles.py`, `scripts/tojpg.py`,
`analyses/05_by_raw_image/by_experiment.qmd`

### `randomised_info.csv` — generated
Produced by `scripts/allocations.py` (which shuffles images and calculates CDA
batch counts), with `scorer1`, `scorer2`, `scorer3` columns added manually
afterwards using the staggered allocation pattern. Contains one row per raw
agroinfiltration image across both dataset parts.

| Column   | Description                                          |
|----------|------------------------------------------------------|
| Set      | Dataset part (1 or 2)                                |
| index    | Original row index from image_paths.csv              |
| Path     | Full path to TIF file on shared drive                |
| count    | Estimated CDA count (from image_info.csv)            |
| basename | TIF filename                                         |
| scorer1  | First assigned scorer name                           |
| scorer2  | Second assigned scorer name                          |
| scorer3  | Third assigned scorer name                           |

Used by: `scripts/movefiles.py`, `scripts/tojpg.py`,
`analyses/01_generate_raw_data/02_combining_cdascorer_outputs/combine_cdascorer.qmd`,
`analyses/05_by_raw_image/by_experiment.qmd`

## Generating these files from scratch

1. List all TIF files on the shared drive and save paths to `image_paths.csv`
2. Populate `image_info.csv` manually for the new dataset part
3. Run `allocations.py` (with `SET` and `N_SCORERS` set correctly) → `randomised_info.csv`
4. Add `scorer1`, `scorer2`, `scorer3` columns to `randomised_info.csv` manually
5. Run `scripts/movefiles.py` (with `SET` set correctly) to distribute images to scorer folders
