import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

from annotation_viewer import save_annotation_image, save_all_annotation_images


@pytest.fixture
def sample_rows():
    return pd.DataFrame({
        'Basename':  ['img.tif', 'img.tif'],
        'Row':       [1, 1],
        'Col':       [1, 2],
        'Pos':       [1, 1],
        'Scorer1':   ['Alice', 'Alice'],
        'Score1':    [3.0, 0.0],
        'X1_1': [100, 200], 'X2_1': [200, 300], 'Y1_1': [100, 200], 'Y2_1': [200, 300],
        'Scorer2':   ['Bob', 'Bob'],
        'Score2':    [3.0, 0.0],
        'X1_2': [110, 210], 'X2_2': [210, 310], 'Y1_2': [110, 210], 'Y2_2': [210, 310],
        'Scorer3':   ['Carol', None],
        'Score3':    [2.0, np.nan],
        'X1_3': [120, np.nan], 'X2_3': [220, np.nan],
        'Y1_3': [120, np.nan], 'Y2_3': [220, np.nan],
    })


@pytest.fixture
def mock_image():
    return Image.new('RGB', (600, 400), color=(80, 120, 60))


class TestSaveAnnotationImage:

    def test_creates_output_file(self, sample_rows, mock_image, tmp_path):
        with patch('annotation_viewer.Image.open', return_value=mock_image):
            output = tmp_path / 'test.jpg'
            save_annotation_image('img.tif', sample_rows, '/fake/path', output)
            assert output.exists()

    def test_missing_scorer_coords_do_not_raise(self, sample_rows, mock_image, tmp_path):
        with patch('annotation_viewer.Image.open', return_value=mock_image):
            output = tmp_path / 'test.jpg'
            save_annotation_image('img.tif', sample_rows, '/fake/path', output)
            assert output.exists()

    def test_creates_parent_dirs(self, sample_rows, mock_image, tmp_path):
        with patch('annotation_viewer.Image.open', return_value=mock_image):
            output = tmp_path / 'subdir' / 'test.jpg'
            save_annotation_image('img.tif', sample_rows, '/fake/path', output)
            assert output.exists()

    def test_all_scorers_missing_coords(self, mock_image, tmp_path):
        rows = pd.DataFrame({
            'Basename': ['img.tif'],
            'Row': [1], 'Col': [1], 'Pos': [1],
            'Scorer1': ['Alice'], 'Score1': [3.0],
            'X1_1': [np.nan], 'X2_1': [np.nan], 'Y1_1': [np.nan], 'Y2_1': [np.nan],
            'Scorer2': [np.nan], 'Score2': [np.nan],
            'X1_2': [np.nan], 'X2_2': [np.nan], 'Y1_2': [np.nan], 'Y2_2': [np.nan],
            'Scorer3': [np.nan], 'Score3': [np.nan],
            'X1_3': [np.nan], 'X2_3': [np.nan], 'Y1_3': [np.nan], 'Y2_3': [np.nan],
        })
        with patch('annotation_viewer.Image.open', return_value=mock_image):
            output = tmp_path / 'test.jpg'
            save_annotation_image('img.tif', rows, '/fake/path', output)
            assert output.exists()


class TestSaveAllAnnotationImages:

    @pytest.fixture
    def two_image_data(self):
        def make_row(basename, col):
            return {
                'Basename': basename, 'Row': 1, 'Col': col, 'Pos': 1,
                'Scorer1': 'Alice', 'Score1': 3.0,
                'X1_1': 100, 'X2_1': 200, 'Y1_1': 100, 'Y2_1': 200,
                'Scorer2': np.nan, 'Score2': np.nan,
                'X1_2': np.nan, 'X2_2': np.nan, 'Y1_2': np.nan, 'Y2_2': np.nan,
                'Scorer3': np.nan, 'Score3': np.nan,
                'X1_3': np.nan, 'X2_3': np.nan, 'Y1_3': np.nan, 'Y2_3': np.nan,
            }
        return pd.DataFrame([
            make_row('img1.tif', 1),
            make_row('img1.tif', 2),
            make_row('img2.tif', 1),
        ])

    def test_creates_one_file_per_image(self, two_image_data, tmp_path):
        mock_img = Image.new('RGB', (500, 400))
        with patch('annotation_viewer.Image.open', return_value=mock_img):
            save_all_annotation_images(two_image_data, '/fake/path', tmp_path)
        assert (tmp_path / 'img1_annotations.jpg').exists()
        assert (tmp_path / 'img2_annotations.jpg').exists()

    def test_creates_output_dir_if_missing(self, two_image_data, tmp_path):
        new_dir = tmp_path / 'new'
        assert not new_dir.exists()
        mock_img = Image.new('RGB', (500, 400))
        with patch('annotation_viewer.Image.open', return_value=mock_img):
            save_all_annotation_images(two_image_data, '/fake/path', new_dir)
        assert new_dir.exists()

    def test_output_filename_strips_extension(self, two_image_data, tmp_path):
        mock_img = Image.new('RGB', (500, 400))
        with patch('annotation_viewer.Image.open', return_value=mock_img):
            save_all_annotation_images(two_image_data, '/fake/path', tmp_path)
        files = {f.name for f in tmp_path.iterdir()}
        assert 'img1_annotations.jpg' in files
        assert 'img1.tif_annotations.jpg' not in files
