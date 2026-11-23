# UV Agroinfiltration Dataset

[![Tests](https://github.com/joshuandwilliams/uv-agroinfiltration-dataset/actions/workflows/test.yml/badge.svg)](https://github.com/joshuandwilliams/uv-agroinfiltration-dataset/actions/workflows/test.yml)
[![Lint](https://github.com/joshuandwilliams/uv-agroinfiltration-dataset/actions/workflows/lint.yml/badge.svg)](https://github.com/joshuandwilliams/uv-agroinfiltration-dataset/actions/workflows/lint.yml)
[![Codecov test coverage](https://codecov.io/gh/joshuandwilliams/uv-agroinfiltration-dataset/graph/badge.svg)](https://app.codecov.io/gh/joshuandwilliams/uv-agroinfiltration-dataset)
![python](https://img.shields.io/badge/python-3.12-1e90ff?logo=python)
![R](https://img.shields.io/badge/R-4.4-1e90ff?logo=r)

This repository builds and analyses a dataset of 6,364 cell death area (CDA)
images from UV agroinfiltration experiments in *Nicotiana benthamiana*. Three
raters scored each CDA for cell death severity, from 0 (no cell death) to 6
(strong cell death). The analyses measure how well the raters agree and what
makes a CDA hard to score. They are the results of Chapter 2 of the thesis.

## Dataset

The images, bounding boxes and each rater's scores will be archived on Zenodo
at [10.5281/zenodo.20493034](https://doi.org/10.5281/zenodo.20493034). The DOI
works once the record is published. Raters are identified by ID only.

## What is here

| Path | Contents |
|---|---|
| `src/` | Python and R helpers: dataset preparation, rater performance, agreement metrics, resampling and plotting |
| `analyses/` | Quarto analyses, numbered in the order of Chapter 2's results (see below) |
| `scripts/` | Anonymising the raw rater files, drawing leaf-sector outlines, and uploading to Zenodo |
| `data/` | The anonymised raw rater files (`cdascorer_anon/`) and the extracted image features (`features/`). The images themselves are not tracked |
| `tests/` | pytest tests for the Python helpers and testthat tests for the R helpers |

The analyses are:

| Folder | Analysis |
|---|---|
| `01_generate_raw_data` | Building the dataset from the raters' raw annotations |
| `02_score_distributions` | The raw annotations and how the scores are distributed |
| `03_human_performance` | How often raters agree with the consensus score |
| `04_project_level_analysis` | Differences between source projects and images, and how images were allocated to raters |
| `05_inter_rater_agreement` | Agreement between raters |
| `06_intra_rater_reliability` | Agreement of raters with their own rescores |
| `07_visual_complexity` | Principal component analysis of the CDA images |
| `08_leaf_positions` | Mean score by position on the leaf |
| `09_image_entropy` | Image information content and the choice of input size |
| `10_segmentation_and_feature_extraction` | Segmenting CDAs from the leaf, extracting hand-crafted features, and predicting scores from them |
| `11_project_feature_differences` | Whether the hand-crafted features differ between source projects |

## Environment

```bash
mamba env create -f environment.yml
mamba activate uv-agroinfiltration
Rscript -e 'install.packages("irrCAC")'
```

`irrCAC` is not on conda-forge, so it is installed from CRAN.
`environment_pinned.yml` lists the exact package builds of a working environment.

## Tests

```bash
pip install -e '.[test]'
pytest
Rscript tests/r_coverage.R
```

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

The code is released under the MIT License. See [LICENSE](LICENSE). The
dataset on Zenodo is released under CC BY-NC 4.0.
