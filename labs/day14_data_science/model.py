from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .preprocessing import load_dataset, split_features_target


def train_model(
    dataset_path: Path,
) -> Pipeline:
    dataframe = load_dataset(dataset_path)
    features, target = split_features_target(dataframe)

    x_train, _, y_train, _ = train_test_split(
        features,
        target,
        test_size=0.5,
        random_state=42,
        stratify=target,
    )

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                ),
            ),
        ]
    )

    pipeline.fit(x_train, y_train)

    return pipeline


def save_model(
    model: Pipeline,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(model, output_path)
