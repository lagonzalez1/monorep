import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch
import tempfile
import psutil
from pathlib import Path
from lib.verse.common import get_memory_usage, load_data, get_meter_cols, corr, profile_memory, elapsed_time



class TestCommon(unittest.TestCase):

    def test_get_memory_usage(self):
        """
            Test get_memory_usage function by unit and value must be > 0
            Test expected is almost equal to function usage
        """
        usage = get_memory_usage()
        process = psutil.Process()
        expected_mb = process.memory_info().rss / (1024 ** 2)
        self.assertIsInstance(usage, float)
        self.assertGreater(usage, 0)
        self.assertAlmostEqual(usage, expected_mb)
        

    def test_profile_memory(self):
        expected = "Hello world"
        @profile_memory
        def dummy_function():
            return expected
        actual_return_value = dummy_function()
        assert actual_return_value == expected

    def test_elapsed_time(self):
        expected_return_value = "This function returns a string."
        @elapsed_time
        def dummy_func():
            return expected_return_value

        actual_return_value = dummy_func()
        self.assertEqual(actual_return_value, expected_return_value)

    def test_load_data(self):
        """
            Test load_data with and without **kwargs            
        """
        self.test_load_data_with_kwargs()
        self.test_load_data_without_kwargs()
       
    def test_load_data_without_kwargs(self):
        """
            Test load_data without **kwargs
        """
        csv_data_dummy_data = "col1,col2\n1,a\n2,b"
        with tempfile.NamedTemporaryFile(mode="w+", delete=True, suffix='.csv') as temp_file:
            temp_file.write(csv_data_dummy_data)
            temp_file.seek(0)
            dummy_path = Path(temp_file.name)
            df = load_data(dummy_path)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(df.shape, (2,2))
            self.assertEqual(list(df.columns), ['col1', 'col2'])
            self.assertEqual(df['col1'].dtypes, 'int64')
        
        
    def test_load_data_with_kwargs(self):
        """
            Test load_data passess through **kwargs to pandas.read_csv
        """
        csv_data_dummy_data = "col1,col2\n1,a\n2,b"
        with tempfile.NamedTemporaryFile(mode="w+", delete=True, suffix='.csv') as temp_file:
            temp_file.write(csv_data_dummy_data)
            temp_file.seek(0)
            dummy_path = Path(temp_file.name)
            test_kwargs = {
                'sep': ';',
                'header': None,
                'skiprows': 2,
                'encoding': 'utf-8'
            }
            with patch("pandas.read_csv") as mock_read:
                load_data(dummy_path, **test_kwargs)
                mock_read.assert_called_once_with(dummy_path, **test_kwargs)
                
    def test_get_meter_cols(self):
        """
            Test get_meter_cols by expected units.
        """
        df = pd.DataFrame({
            "MT_one": [1,2,3],
            "MT_two": [1,2,3],
            "MT_three": [1,2,3],
            "MT_four": [1,2,3],
        })
        cols = get_meter_cols(df)
        self.assertListEqual(cols, ["MT_one", "MT_two", "MT_three", "MT_four"])
        self.assertIsInstance(cols, list)


    def test_corr1(self):
        df = pd.DataFrame({
            "MT_x": [1,2,3],
            "MT_y": [1,2,3]
        })
        cols = get_meter_cols(df)
        mat = corr(df, cols)
        self.assertIsInstance(mat, np.ndarray)
        self.assertEqual(mat.shape, (2,2))


    def test_corr2(self):
        """
            Test get_meter_cols by diagonal and Pearson correlation            
            Ref: 
            https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_allclose.html
            https://muthu.co/understanding-correlations-and-correlation-matrix/
            https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html#numpy-corrcoef
        """
        df = pd.DataFrame({
            "MT_w": [1,2,3],
            "MT_x": [3,2,1],
            "MT_y": [1,2,3],
            "MT_z": [3,2,1],          
        })
        cols = get_meter_cols(df)
        mat = corr(df, cols)
        # Compare Matrix A with B, diagonal must be 1
        np.testing.assert_allclose(np.diag(mat), np.ones(4))
        # Pearson correlation matrix
        self.assertAlmostEqual(mat[0,1], -1.0, places=6)

if __name__ == "__main__":
    unittest.main()
