from pathlib import Path

import pandas as pd

from labs.day14_data_science.inference import predict
from labs.day14_data_science.model import save_model, train_model
from labs.day14_data_science.preprocessing import (
    load_dataset,
    split_features_target,
)

DATASET_PATH = Path("labs/day14_data_science/data/iris.csv")


def test_load_dataset():
    dataframe = load_dataset(DATASET_PATH)

    assert not dataframe.empty
    assert dataframe.isna().sum().sum() == 0


def test_split_features_target():
    dataframe = load_dataset(DATASET_PATH)

    features, target = split_features_target(dataframe)

    assert isinstance(features, pd.DataFrame)
    assert len(features) == len(target)
    assert list(features.columns) == [
        "sepal_length",
        "sepal_width",
        "petal_length",
        "petal_width",
    ]


def test_train_and_predict(tmp_path):
    model = train_model(DATASET_PATH)

    model_path = tmp_path / "model.joblib"
    save_model(model, model_path)

    assert model_path.exists()

    result = predict(
        model,
        {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
    )

    assert result in {
        "setosa",
        "versicolor",
        "virginica",
    }
