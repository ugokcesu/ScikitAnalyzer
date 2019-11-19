from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

import pandas as pd

from ml_choices import MLRegression, MLClassification, Scalers
from scikit_logger import ScikitLogger


class DummyEstimator(BaseEstimator):
    def fit(self):
        pass

    def score(self):
        pass


class DummyScaler(BaseEstimator, TransformerMixin):
    def fit(self):
        pass

    def transform(self):
        pass


class NoneScaler(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X


class MLExpert:
    def __init__(self, ds):
        self._ds = ds
        self._grid = None
        self._logger = ScikitLogger()
        self._results_df = None

    def big_loop(self, feature_columns, target_column, test_ratio, scalers, parameters, categorical):
        X_train, X_test, y_train, y_test = self.data_splitter(test_ratio, feature_columns, target_column, categorical)

        pipeline = self.assemble_pipeline('DummyScaler', 'DummyEstimator')

        combined_parameters = self.combine_parameters(scalers, parameters)

        grid = GridSearchCV(pipeline, combined_parameters, n_jobs=-2, return_train_score=True, cv=5, iid=False)
        grid.fit(X_train, y_train)

        df = pd.DataFrame(grid.cv_results_)

        self._results_df = df
        self._grid = grid
        return self._grid
        # all fitting is done, results inside grids

    @classmethod
    def class_factory(cls, class_name):
        return globals()[class_name]()

    def data_splitter(self, test_ratio, feature_columns, target_column, categorical):
        all_x, all_y = self._ds.df[feature_columns], self._ds.df[target_column]
        if categorical:
            X_train, X_test, y_train, y_test = train_test_split(all_x, all_y, stratify=all_y)
        else:
            X_train, X_test, y_train, y_test = train_test_split(all_x, all_y, test_size=test_ratio)
        return X_train, X_test, y_train, y_test

    def assemble_pipeline(self,  scaler, ml):
        steps = []
        if scaler != 'None':
            steps.append((scaler, self.class_factory(scaler)))

        steps.append((ml, self.class_factory(ml)))

        pipeline = Pipeline(steps=steps)
        return pipeline

    def combine_parameters(self, scalers, parameters):
        final_list = []
        for scaler in scalers:
            for ml, params in parameters.items():
                new_parameters = {}
                # 1 add ml parameters
                for key, val in params.items():
                    new_parameters['DummyEstimator__' + key] = val
                # 2 add ml itself
                new_parameters['DummyEstimator'] = [self.class_factory(ml)]
                # 3 add scaler
                if scaler == 'None':
                    new_parameters['DummyScaler'] = [self.class_factory('NoneScaler')]
                else:
                    new_parameters['DummyScaler'] = [self.class_factory(scaler)]
                # finally add dict to list
                final_list.append(new_parameters)
        return final_list
