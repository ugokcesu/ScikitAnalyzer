from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

import pandas as pd
import numpy as np
from copy import deepcopy
from collections import defaultdict

from ml_choices import MLRegression, MLClassification, Scalers
from scikit_logger import ScikitLogger
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
    logger = ScikitLogger()
    def __init__(self, ds):
        self._ds = ds
        self._grid = None
        self._logger = ScikitLogger()
        self._results_df = None

    def big_loop(self, feature_columns, target_column, test_ratio, scalers, parameters, categorical):
        #X_train, X_test, y_train, y_test = self.data_splitter(test_ratio, feature_columns, target_column, categorical)
        y_train = self._ds.df[target_column]
        X_train = self._ds.df[feature_columns]
        if len(feature_columns) == 1:
            X_train.values.reshape(-1,1)

        if categorical:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)
        else:
            cv = KFold(n_splits=5, shuffle=True, random_state=1)

        pipeline = self.assemble_pipeline('DummyScaler', 'DummyEstimator')

        combined_parameters = self.combine_parameters(scalers, parameters)

        grid = GridSearchCV(pipeline, combined_parameters, return_train_score=True, cv=cv,
                             error_score='raise')
        # parameters validated, but still scikit may throw an exception
        try:
            grid.fit(X_train, y_train)
        except Exception as e:
            self.logger.exception(e)
            return None

        df = pd.DataFrame(grid.cv_results_)

        self._results_df = df
        self._grid = grid
        return self._grid, self._results_df
        # all fitting is done, results inside grids

    def feature_uncertainty_loop(self, feature_columns, target_column, test_ratio, scalers, parameters, categorical):
        # X_train, X_test, y_train, y_test = self.data_splitter(test_ratio, feature_columns, target_column, categorical)
        if categorical:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)
        else:
            cv = KFold(n_splits=5, shuffle=True, random_state=1)

        y_train = self._ds.df[target_column]
        pipeline = self.assemble_pipeline('DummyScaler', 'DummyEstimator')
        combined_parameters = self.combine_parameters(scalers, parameters)
        grid = GridSearchCV(pipeline, combined_parameters,  return_train_score=True, cv=cv,
                             error_score='raise')

        # start looping through feature_columns
        df_list = []
        for cols in feature_columns:
            X_train = self._ds.df[cols]
            if len(cols) == 1:
                X_train.values.reshape(-1, 1)
            try:
                grid.fit(X_train, y_train)
            except Exception as e:
                self.logger.exception(e)
                return None
            df = pd.DataFrame(grid.cv_results_)
            df['columns'] = [cols for _ in range(len(df))]
            df_list.append(df)
        df_results = pd.concat(df_list)
        df_results = df_results.reset_index(drop=True)
        return df_results
        # all fitting is done, results inside grids

    @staticmethod
    def compute_added_value(unc_df, secondary, all_combinations):
        #unc_df = unc_df.reset_index(drop=True)
        val_added = defaultdict(list)
        for feature in secondary:
            for combination in all_combinations:
                if feature in combination:
                    #if the only feature in combination is feature, skip it
                    if len(combination) == 1:
                        continue
                    # else, compute score with and without feature
                    idx = unc_df[unc_df['columns'].apply(lambda x: x == combination)].index[0]
                    score_w_feat = unc_df.iloc[idx]['mean_test_score']
                    combin_wo_feat = deepcopy(combination)
                    combin_wo_feat.remove(feature)
                    idx = unc_df[unc_df['columns'].apply(lambda x: x == combin_wo_feat)].index[0]
                    score_wo_feat = unc_df.iloc[idx]['mean_test_score']
                    value_added = score_w_feat - score_wo_feat
                    val_added[feature].append(value_added)
        return val_added


    @classmethod
    def class_factory(cls, class_name):
        return globals()[class_name]()

    def data_splitter(self, test_ratio, feature_columns, target_column, categorical):
        all_x, all_y = self._ds.df[feature_columns], self._ds.df[target_column]
        if categorical:
            X_train, X_test, y_train, y_test = train_test_split(all_x, all_y, test_size=test_ratio, stratify=all_y, shuffle=False)
        else:
            X_train, X_test, y_train, y_test = train_test_split(all_x, all_y, test_size=test_ratio, shuffle=False)
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
