from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from .preprocessing import FEATURE_COLUMNS


def load_model(path: Path) -> Pipeline:
    return joblib.load(path)


def predict(
    model: Pipeline,
    values: dict[str, float],
) -> str:
    dataframe = pd.DataFrame(
        [values],
        columns=FEATURE_COLUMNS,
    )

    prediction = model.predict(dataframe)

    return str(prediction[0])
