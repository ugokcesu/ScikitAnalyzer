from enum import Enum


class Scalers(Enum):
    MinMax = 1
    Robust = 2

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


class MLRegression(Enum):
    KNeighborsRegressor = 1
    SVR = 2

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


class MLClassification(Enum):
    KNeighborsClassifier = 1
    SVC = 2

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


class MLWidgets(Enum):
    KNeighbors = 1
    SV = 2

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


def ml_2_widgets(ml):
    matching = {
        MLRegression.SVR.name:     MLWidgets.SV,
        MLClassification.SVC.name: MLWidgets.SV,
        MLRegression.KNeighborsRegressor.name: MLWidgets.KNeighbors,
        MLClassification.KNeighborsClassifier.name: MLWidgets.KNeighbors
    }
    if ml not in matching.keys():
        return None
    else:
        return matching[ml]
