from sklearn.model_selection import train_test_split
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

from ml_choices import MLRegression, MLClassification, Scalers
from scikit_logger import ScikitLogger


class MLExpert:
    def __init__(self, ds):
        self._ds = ds
        self._logger = ScikitLogger()
        self._scalers = {Scalers.MinMax.name: MinMaxScaler(), Scalers.Robust.name: RobustScaler()}
        self._ml = {MLClassification.KNeighborsClassifier.name: KNeighborsClassifier(), MLClassification.SVC.name: SVC(),
                    MLRegression.KNeighborsRegressor.name: KNeighborsRegressor(), MLRegression.SVR.name: SVR()}

    def data_splitter(self, ml, test_ratio, feature_columns, target_column):
        all_x, all_y = self._ds.df[feature_columns], self._ds.df[target_column]
        if ml in MLClassification.all_values():
            X_train, X_test, y_train, y_test = train_test_split(all_x, all_y, stratify=all_y)
        else:
            X_train, X_test, y_train, y_test = train_test_split(all_x, all_y, test_size=test_ratio)
        return X_train, X_test, y_train, y_test

    def assemble_pipeline(self,  scaler, ml):
        steps = []
        if scaler in self._scalers.keys():
            steps.append((scaler, self._scalers[scaler]))

        if ml in self._ml.keys():
            steps.append((ml, self._ml[ml]))

        pipeline = Pipeline(steps=steps)
        return pipeline

    def fit_grid(self, ml, pipeline, parameters, X_train, y_train):
        new_parameters = {}
        for key, val in parameters.items():
            new_parameters[ml + '__' + key] = val

        grid = GridSearchCV(pipeline, new_parameters, n_jobs=1, cv=3, verbose=3)
        grid.fit(X_train.values, y_train.values)
        return grid









