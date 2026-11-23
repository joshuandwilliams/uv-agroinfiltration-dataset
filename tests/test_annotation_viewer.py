from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from annotation_viewer import (
    _draw_score_label_pil,
    save_all_annotation_images,
    save_annotation_image,
)


@pytest.fixture
def sample_rows():
    return pd.DataFrame(
        {
            "Basename": ["img.tif", "img.tif"],
            "Row": [1, 1],
            "Col": [1, 2],
            "Pos": [1, 1],
            "Scorer1": ["Alice", "Alice"],
            "Score1": [3.0, 0.0],
            "X1_1": [100, 200],
            "X2_1": [200, 300],
            "Y1_1": [100, 200],
            "Y2_1": [200, 300],
            "Scorer2": ["Bob", "Bob"],
            "Score2": [3.0, 0.0],
            "X1_2": [110, 210],
            "X2_2": [210, 310],
            "Y1_2": [110, 210],
            "Y2_2": [210, 310],
            "Scorer3": ["Carol", None],
            "Score3": [2.0, np.nan],
            "X1_3": [120, np.nan],
            "X2_3": [220, np.nan],
            "Y1_3": [120, np.nan],
            "Y2_3": [220, np.nan],
        }
    )


@pytest.fixture
def mock_image():
    return Image.new("RGB", (600, 400), color=(80, 120, 60))


class TestSaveAnnotationImage:

    def test_creates_output_file(self, sample_rows, mock_image, tmp_path):
        with patch("annotation_viewer.Image.open", return_value=mock_image):
            output = tmp_path / "test.jpg"
            save_annotation_image("img.tif", sample_rows, "/fake/path", output)
            assert output.exists()

    def test_missing_scorer_coords_do_not_raise(self, sample_rows, mock_image, tmp_path):
        with patch("annotation_viewer.Image.open", return_value=mock_image):
            output = tmp_path / "test.jpg"
            save_annotation_image("img.tif", sample_rows, "/fake/path", output)
            assert output.exists()

    def test_creates_parent_dirs(self, sample_rows, mock_image, tmp_path):
        with patch("annotation_viewer.Image.open", return_value=mock_image):
            output = tmp_path / "subdir" / "test.jpg"
            save_annotation_image("img.tif", sample_rows, "/fake/path", output)
            assert output.exists()

    def test_all_scorers_missing_coords(self, mock_image, tmp_path):
        rows = pd.DataFrame(
            {
                "Basename": ["img.tif"],
                "Row": [1],
                "Col": [1],
                "Pos": [1],
                "Scorer1": ["Alice"],
                "Score1": [3.0],
                "X1_1": [np.nan],
                "X2_1": [np.nan],
                "Y1_1": [np.nan],
                "Y2_1": [np.nan],
                "Scorer2": [np.nan],
                "Score2": [np.nan],
                "X1_2": [np.nan],
                "X2_2": [np.nan],
                "Y1_2": [np.nan],
                "Y2_2": [np.nan],
                "Scorer3": [np.nan],
                "Score3": [np.nan],
                "X1_3": [np.nan],
                "X2_3": [np.nan],
                "Y1_3": [np.nan],
                "Y2_3": [np.nan],
            }
        )
        with patch("annotation_viewer.Image.open", return_value=mock_image):
            output = tmp_path / "test.jpg"
            save_annotation_image("img.tif", rows, "/fake/path", output)
            assert output.exists()


class TestSaveAllAnnotationImages:

    @pytest.fixture
    def two_image_data(self):
        def make_row(basename, col):
            return {
                "Basename": basename,
                "Row": 1,
                "Col": col,
                "Pos": 1,
                "Scorer1": "Alice",
                "Score1": 3.0,
                "X1_1": 100,
                "X2_1": 200,
                "Y1_1": 100,
                "Y2_1": 200,
                "Scorer2": np.nan,
                "Score2": np.nan,
                "X1_2": np.nan,
                "X2_2": np.nan,
                "Y1_2": np.nan,
                "Y2_2": np.nan,
                "Scorer3": np.nan,
                "Score3": np.nan,
                "X1_3": np.nan,
                "X2_3": np.nan,
                "Y1_3": np.nan,
                "Y2_3": np.nan,
            }

        return pd.DataFrame(
            [
                make_row("img1.tif", 1),
                make_row("img1.tif", 2),
                make_row("img2.tif", 1),
            ]
        )

    def test_creates_one_file_per_image(self, two_image_data, tmp_path):
        mock_img = Image.new("RGB", (500, 400))
        with patch("annotation_viewer.Image.open", return_value=mock_img):
            save_all_annotation_images(two_image_data, "/fake/path", tmp_path)
        assert (tmp_path / "img1_annotations.jpg").exists()
        assert (tmp_path / "img2_annotations.jpg").exists()

    def test_creates_output_dir_if_missing(self, two_image_data, tmp_path):
        new_dir = tmp_path / "new"
        assert not new_dir.exists()
        mock_img = Image.new("RGB", (500, 400))
        with patch("annotation_viewer.Image.open", return_value=mock_img):
            save_all_annotation_images(two_image_data, "/fake/path", new_dir)
        assert new_dir.exists()

    def test_output_filename_strips_extension(self, two_image_data, tmp_path):
        mock_img = Image.new("RGB", (500, 400))
        with patch("annotation_viewer.Image.open", return_value=mock_img):
            save_all_annotation_images(two_image_data, "/fake/path", tmp_path)
        files = {f.name for f in tmp_path.iterdir()}
        assert "img1_annotations.jpg" in files
        assert "img1.tif_annotations.jpg" not in files


class TestFallbacksAndSkips:
    def test_label_width_without_getlength(self, sample_rows):
        # Fonts without getlength() fall back to an estimate from the font size
        draw = MagicMock()
        _draw_score_label_pil(draw, sample_rows.iloc[0], 0, 0, font=object(), font_size=10)
        xs = [c.args[0][0] for c in draw.text.call_args_list]
        assert xs == sorted(xs) and xs[1] == 6  # "[" is estimated as 0.6 x 10 px

    def test_skip_existing_leaves_file_untouched(self, sample_rows, tmp_path):
        out = tmp_path / "done.jpg"
        out.write_bytes(b"old")
        with patch("annotation_viewer.Image.open") as opener:
            save_annotation_image("img.tif", sample_rows, tmp_path, out, skip_existing=True)
        opener.assert_not_called()
        assert out.read_bytes() == b"old"

    def test_default_font_when_helvetica_is_missing(self, sample_rows, mock_image, tmp_path):
        from PIL import ImageFont

        real_truetype = ImageFont.truetype

        def no_helvetica(font, *args, **kwargs):
            if font == "/System/Library/Fonts/Helvetica.ttc":
                raise OSError("not on this system")
            return real_truetype(font, *args, **kwargs)  # load_default() uses truetype too

        out = tmp_path / "out.jpg"
        with (
            patch("annotation_viewer.Image.open", return_value=mock_image),
            patch("annotation_viewer.ImageFont.truetype", side_effect=no_helvetica),
        ):
            save_annotation_image("img.tif", sample_rows, tmp_path, out)
        assert out.exists()

    def test_save_all_skips_existing_outputs(self, sample_rows, tmp_path, capsys):
        (tmp_path / "img_annotations.jpg").write_bytes(b"old")
        with patch("annotation_viewer.Image.open") as opener:
            save_all_annotation_images(sample_rows, tmp_path, tmp_path, skip_existing=True)
        opener.assert_not_called()
        assert "Skipping img_annotations.jpg" in capsys.readouterr().out
