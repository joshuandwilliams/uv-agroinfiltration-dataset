import json
import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

from coco_export import generate_coco_json, generate_multi_rater_csv



@pytest.fixture
def median_data():
    return pd.DataFrame({
        "Basename": ["img1.tif", "img1.tif", "img2.tif"],
        "Row":      [1, 1, 2],
        "Col":      [1, 2, 1],
        "Pos":      [1, 1, 1],
        "Median_Score": [0.0, 3.0, 6.0],
    })


@pytest.fixture
def median_df():
    return pd.DataFrame({
        "Basename": ["img1.tif", "img2.tif"],
        "Row": [1, 1], "Col": [1, 2], "Pos": [1, 1],
        "Median_Score": [3.0, 0.0],
        "Scorer1": [1, 1], "Score1": [3.0, 0.0],
        "X1_1": [100, 200], "X2_1": [200, 300], "Y1_1": [100, 200], "Y2_1": [200, 300],
        "Scorer2": [2, 2], "Score2": [3.0, 0.0],
        "X1_2": [110, 210], "X2_2": [210, 310], "Y1_2": [110, 210], "Y2_2": [210, 310],
        "Scorer3": [pd.NA, pd.NA], "Score3": [pd.NA, pd.NA],
        "X1_3": [pd.NA, pd.NA], "X2_3": [pd.NA, pd.NA],
        "Y1_3": [pd.NA, pd.NA], "Y2_3": [pd.NA, pd.NA],
    })


@pytest.fixture
def mock_image():
    return Image.new("RGB", (234, 234))


class TestGenerateCocoJson:

    def test_creates_valid_json(self, median_data, mock_image, tmp_path):
        with patch("coco_export.Image.open", return_value=mock_image):
            output = tmp_path / "coco.json"
            generate_coco_json(median_data, tmp_path, output)
            assert output.exists()
            with open(output) as f:
                coco = json.load(f)
            assert "info" in coco
            assert "images" in coco
            assert "annotations" in coco
            assert "categories" in coco

    def test_image_and_annotation_counts_match(self, median_data, mock_image, tmp_path):
        with patch("coco_export.Image.open", return_value=mock_image):
            output = tmp_path / "coco.json"
            generate_coco_json(median_data, tmp_path, output)
            coco = json.load(open(output))
            assert len(coco["images"]) == len(median_data)
            assert len(coco["annotations"]) == len(median_data)

    def test_categories_cover_0_to_6(self, median_data, mock_image, tmp_path):
        with patch("coco_export.Image.open", return_value=mock_image):
            output = tmp_path / "coco.json"
            generate_coco_json(median_data, tmp_path, output)
            coco = json.load(open(output))
            cat_ids = {c["id"] for c in coco["categories"]}
            assert cat_ids == set(range(7))

    def test_annotation_category_matches_median_score(self, median_data, mock_image, tmp_path):
        with patch("coco_export.Image.open", return_value=mock_image):
            output = tmp_path / "coco.json"
            generate_coco_json(median_data, tmp_path, output)
            coco = json.load(open(output))
            for ann, score in zip(coco["annotations"], median_data["Median_Score"]):
                assert ann["category_id"] == int(score)

    def test_image_ids_are_unique(self, median_data, mock_image, tmp_path):
        with patch("coco_export.Image.open", return_value=mock_image):
            output = tmp_path / "coco.json"
            generate_coco_json(median_data, tmp_path, output)
            coco = json.load(open(output))
            ids = [img["id"] for img in coco["images"]]
            assert len(ids) == len(set(ids))

    def test_cc_by_nc_license(self, median_data, mock_image, tmp_path):
        with patch("coco_export.Image.open", return_value=mock_image):
            output = tmp_path / "coco.json"
            generate_coco_json(median_data, tmp_path, output)
            coco = json.load(open(output))
            assert any("NonCommercial" in lic["name"] for lic in coco["licenses"])


class TestGenerateMultiRaterCsv:

    def test_creates_output_file(self, median_df, tmp_path):
        output = tmp_path / "multi_rater.csv"
        generate_multi_rater_csv(median_df, output)
        assert output.exists()

    def test_one_row_per_annotation(self, median_df, tmp_path):
        # 2 CDAs × 2 valid scorers each = 4 annotation rows
        output = tmp_path / "multi_rater.csv"
        generate_multi_rater_csv(median_df, output)
        df = pd.read_csv(output)
        assert len(df) == 4

    def test_includes_median_score_and_bbox(self, median_df, tmp_path):
        output = tmp_path / "multi_rater.csv"
        generate_multi_rater_csv(median_df, output)
        df = pd.read_csv(output)
        for col in ["Median_Score", "Scorer_ID", "Score", "X1", "X2", "Y1", "Y2"]:
            assert col in df.columns

    def test_missing_scorer_rows_excluded(self, median_df, tmp_path):
        output = tmp_path / "multi_rater.csv"
        generate_multi_rater_csv(median_df, output)
        df = pd.read_csv(output)
        assert df["Scorer_ID"].notna().all()
