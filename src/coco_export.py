"""
Generate COCO-format JSON and anonymised multi-rater CSV for Zenodo upload.

The COCO JSON uses median scores as the annotation category.
The multi-rater CSV uses the score_table pivot format (one column per scorer ID)
so it can be used directly for inter-rater reliability analyses.
"""
import json
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from PIL import Image


def generate_coco_json(
    median_data: pd.DataFrame,
    images_dir: Path,
    output_path: Path,
    info: Optional[Dict] = None,
) -> None:
    """
    Generate a COCO-format JSON for the CDA dataset.

    Each entry in median_data becomes one image + one annotation.
    The annotation category_id is the integer median score (0–6).

    Parameters
    ----------
    median_data : pd.DataFrame
        combined_cda_data_median.csv — must have Basename, Row, Col, Pos,
        Median_Score columns.
    images_dir : Path
        Root of the cropped image directory (data/cropped_images/).
        Images are expected at images_dir/<score>/<stem>_<row>_<col>_<pos>.tif
    output_path : Path
        Destination path for the JSON file.
    info : dict, optional
        Dataset info block. Defaults to standard dataset description.
    """
    info = info or {
        "description": (
            "UV-spectra agroinfiltration cell death area (CDA) image dataset. "
            "6,336 cropped CDA images annotated by up to 10 human scorers on a "
            "0–6 severity scale. Median score used as ground truth label."
        ),
        "version": "1.0",
        "year": 2025,
        "contributor": "Joshua Williams",
        "date_created": "2025",
    }

    licenses = [{
        "id": 1,
        "name": "Creative Commons Attribution-NonCommercial 4.0 International",
        "url": "https://creativecommons.org/licenses/by-nc/4.0/",
    }]

    categories = [
        {"id": i, "name": str(i), "supercategory": "cell_death_severity"}
        for i in range(7)
    ]

    images, annotations = [], []

    for image_id, row in enumerate(median_data.itertuples(), start=1):
        stem = Path(row.Basename).stem
        score = int(row.Median_Score)
        filename = f"{stem}_{row.Row}_{row.Col}_{row.Pos}.tif"
        file_path = Path(images_dir) / str(score) / filename

        with Image.open(file_path) as img:
            width, height = img.size

        images.append({
            "id": image_id,
            "file_name": f"{score}/{filename}",
            "width": width,
            "height": height,
            "license": 1,
        })

        annotations.append({
            "id": image_id,
            "image_id": image_id,
            "category_id": score,
        })

    coco = {
        "info": info,
        "licenses": licenses,
        "categories": categories,
        "images": images,
        "annotations": annotations,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(coco, f, indent=2)

    print(f"Saved COCO JSON: {len(images)} images, {len(annotations)} annotations → {output_path}")


def generate_multi_rater_csv(
    median_data: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Generate an anonymised multi-rater CSV for Zenodo in long format.

    Produces one row per annotation (CDA × scorer), including the bounding box
    coordinates recorded by each scorer. CDAs with up to three annotations each
    are covered. Scorer identities are anonymised integer IDs.

    Parameters
    ----------
    median_data : pd.DataFrame
        combined_cda_data_median.csv — must contain Basename, Row, Col, Pos,
        Median_Score, Scorer1-3 (anonymised IDs), Score1-3, X1/X2/Y1/Y2 per scorer.
    output_path : Path
        Destination path for the CSV file.
    """
    id_vars = ["Basename", "Row", "Col", "Pos", "Median_Score"]
    chunks = []
    for i in range(1, 4):
        cols = id_vars + [f"Scorer{i}", f"Score{i}",
                          f"X1_{i}", f"X2_{i}", f"Y1_{i}", f"Y2_{i}"]
        subset = median_data[cols].copy()
        subset.columns = id_vars + ["Scorer_ID", "Score", "X1", "X2", "Y1", "Y2"]
        chunks.append(subset)

    long_df = (
        pd.concat(chunks, ignore_index=True)
        .dropna(subset=["Scorer_ID"])
        .sort_values(["Basename", "Row", "Col", "Pos", "Scorer_ID"])
        .reset_index(drop=True)
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    long_df.to_csv(output_path, index=False)
    n_cdas = long_df[["Basename", "Row", "Col", "Pos"]].drop_duplicates().__len__()
    print(f"Saved multi-rater CSV: {len(long_df)} annotations across {n_cdas} CDAs → {output_path}")
