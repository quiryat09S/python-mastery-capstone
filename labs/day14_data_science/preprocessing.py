from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width",
]

TARGET_COLUMN = "species"


def load_dataset(path: Path) -> pd.DataFrame:
    dataframe = pd.read_csv(path)

    required_columns = [
        *FEATURE_COLUMNS,
        TARGET_COLUMN,
    ]

    missing_columns = set(required_columns) - set(dataframe.columns)

    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")

    dataframe = dataframe.dropna(subset=required_columns)

    for column in FEATURE_COLUMNS:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe = dataframe.dropna(subset=FEATURE_COLUMNS)

    return dataframe


def split_features_target(
    dataframe: pd.DataFrame,
):
    features = dataframe[FEATURE_COLUMNS]
    target = dataframe[TARGET_COLUMN]

    return features, target
