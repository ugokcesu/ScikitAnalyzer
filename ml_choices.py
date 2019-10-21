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
