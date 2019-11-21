import sys
from unittest import TestCase

from PyQt5.Qt import QApplication

from gui.feature_analysis_tab import FeatureAnalysisTab


class TestFeatureAnalysisTab(TestCase):
    def test_full_factorial_combination(self):
        app = QApplication(sys.argv)
        FAT = FeatureAnalysisTab()
        result = FAT.full_factorial_combination([1,2,3], [[]])
        answer = [[1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
        self.assertListEqual(result, answer)

