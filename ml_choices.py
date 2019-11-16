from enum import Enum


class Scalers(Enum):
    MinMax = 0
    Robust = 1

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


class MLRegression(Enum):
    KNeighborsRegressor = 0
    SVR = 1

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


class MLClassification(Enum):
    KNeighborsClassifier = 0
    SVC = 1

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


class MLWidgets(Enum):
    KNeighbors = 0
    SV = 1

    @classmethod
    def all_values(cls):
        return [m.name for m in cls]


def ml_2_widget_number(ml):
    matching = {
        MLRegression.SVR.name:     MLWidgets.SV,
        MLClassification.SVC.name: MLWidgets.SV,
        MLRegression.KNeighborsRegressor.name: MLWidgets.KNeighbors,
        MLClassification.KNeighborsClassifier.name: MLWidgets.KNeighbors
    }
    if ml not in matching.keys():
        return None
    else:
        return matching[ml].value
