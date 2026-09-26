from pathlib import Path

from .inference import load_model, predict
from .model import save_model, train_model

DATASET_PATH = Path("labs/day14_data_science/data/iris.csv")

MODEL_PATH = Path("labs/day14_data_science/data/iris_model.joblib")


def main() -> None:
    if not MODEL_PATH.exists():
        model = train_model(DATASET_PATH)
        save_model(model, MODEL_PATH)
        print(f"Modelo entrenado y guardado en: {MODEL_PATH}")

    model = load_model(MODEL_PATH)

    sample = {
        "sepal_length": 6.0,
        "sepal_width": 2.7,
        "petal_length": 5.1,
        "petal_width": 1.6,
    }

    result = predict(model, sample)

    print("Inferencia ejecutada correctamente")
    print(f"Entrada: {sample}")
    print(f"Especie predicha: {result}")


if __name__ == "__main__":
    main()
