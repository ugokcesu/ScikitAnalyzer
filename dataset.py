import sklearn
import pandas as pd
import numpy as np


class Dataset:
    def __init__(self, bunch: sklearn.utils.Bunch, name):
        super().__init__()
        self._bunch = bunch
        self._name = name
        # set self._df, the pandas dataframe
        if (not hasattr(self._bunch, 'data')) or (not hasattr(self._bunch, 'target')):
            return None

        if hasattr(self._bunch, 'feature_names'):
            self._df = pd.DataFrame(self._bunch.data, columns=self._bunch.feature_names)
        else:
            self._df = pd.DataFrame(self._bunch.data)
            self._df.columns = self._df.columns.astype(str)

        if hasattr(self._bunch, 'target_names'):
            if len(self._bunch.target.shape) == 1:
                self._df['target'] = self._bunch.target
                self._df['target_names'] = self._df.target.apply(lambda x: self._bunch.target_names[int(x)])
            else:
                for index, name in enumerate(self._bunch.target_names):
                    self._df[name] = self._bunch.target[:, index]
        else:
            self._df['target'] = self._bunch.target

        self._info_df = None
        self._categorical_columns = []
        self._numerical_columns = []
        self._grid = None
        self.update_numericals()

    def update_numericals(self):
        self._numerical_columns = []
        for col in self.column_names():
            if np.issubdtype(self._df[col].dtype, np.number):
                self._numerical_columns.append(col)

    def update_categoricals(self):
        cats = self._categorical_columns
        for cat in cats:
            if cat not in self.column_names():
                self._categorical_columns.remove(cat)

    @property
    def numerical_columns(self):
        return self._numerical_columns

    @property
    def categorical_columns(self):
        return self._categorical_columns

    @categorical_columns.setter
    def categorical_columns(self, v):
        self._categorical_columns = v

    @classmethod
    def create_dataset(cls, bunch, name):
        if (not hasattr(bunch, 'data')) or (not hasattr(bunch, 'target')):
            return None
        else:
            return cls(bunch, name)

    def description(self):
        return self._bunch.DESCR

    @property
    def grid(self):
        return self._grid

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df
        self.update_categoricals()
        self.update_numericals()

    @property
    def name(self):
        return self._name

    @property
    def info_df(self):
        return self._info_df

    def column_names(self):
        return [str(x) for x in self._df.columns]

    def samples(self):
        return self.df.shape[0]
