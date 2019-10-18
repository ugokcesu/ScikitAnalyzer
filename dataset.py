import sklearn
import pandas as pd


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
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df


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
