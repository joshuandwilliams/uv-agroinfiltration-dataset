# UV Agroinfiltration Dataset

[![Lint](https://github.com/joshuandwilliams/uv-agroinfiltration-dataset/actions/workflows/lint.yml/badge.svg)](https://github.com/joshuandwilliams/uv-agroinfiltration-dataset/actions/workflows/lint.yml)
![python](https://img.shields.io/badge/python-3.12-1e90ff?logo=python) ![R](https://img.shields.io/badge/R-4.4-1e90ff?logo=r)

Code behind a dataset of 6,364 UV-spectra agroinfiltration cell death area (CDA) images, each scored 0–6 for severity by three independent raters. Covers dataset construction from raw scorer annotations through to inter-/intra-rater reliability and image-based analyses of scoring difficulty.

## Dataset

The released images, bounding boxes and per-rater scores are archived on Zenodo (<https://doi.org/10.5281/zenodo.20493034>). `data/zenodo/README.md` documents the release files and columns in full.

## What's here

| Path | Contents |
|------|----------|
| `src/` | Dataset preparation, human-performance and agreement-metric helpers (Python + R) |
| `analyses/` | Numbered Quarto analyses: raw annotation visualisation, human rater performance, project-level effects, inter-rater agreement, intra-rater reliability, image PCA, leaf position effects, image entropy, and CDA segmentation/feature extraction |
| `scripts/` | Anonymisation, leaf-sector outline generation, and the Zenodo upload script |
| `data/` | Raw and cropped images, annotations, extracted features, and the Zenodo release bundle |
| `tests/` | pytest and testthat suites for `src/` |

## Environment

```bash
mamba env create -f environment.yml
mamba activate uv-agroinfiltration
```

## Citation

See `CITATION.cff`, or cite the Zenodo record directly (DOI above).

## License

No LICENSE file is included for the code in this repository. The released dataset on Zenodo is CC BY-NC 4.0.
