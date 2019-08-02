import sklearn
import pandas as pd


class Dataset:
    def __init__(self, bunch: sklearn.utils.Bunch):
        super().__init__()
        self._bunch = bunch
        self._df = pd.DataFrame(self._bunch.data, columns=self._bunch.feature_names)
        self._df['target'] = self._bunch.target

    def description(self):
        return self._bunch.DESCR
