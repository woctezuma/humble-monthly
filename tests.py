import unittest

import plot_time_series


class TestPlotTimeSeriesMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(plot_time_series.main())


if __name__ == '__main__':
    unittest.main()
