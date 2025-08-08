import logging
from typing import Dict, Tuple
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from .indicators import add_indicators

logger = logging.getLogger(__name__)


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    df = add_indicators(df.copy())
    df["return"] = df["Close"].pct_change()
    df["next_close"] = df["Close"].shift(-1)
    df["label"] = (df["next_close"] > df["Close"]).astype(int)
    df.dropna(inplace=True)

    feature_cols = [
        "RSI_14",
        "MA_20",
        "MA_50",
        "MACD",
        "MACD_signal",
        "MACD_hist",
        "return",
        "Volume",
        "Volume_Change",
    ]

    X = df[feature_cols]
    y = df["label"]
    return X, y


def train_evaluate(price_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """Train and evaluate ML model using stacking with scaling."""
    accuracies = {}

    for ticker, df in price_data.items():
        try:
            X, y = prepare_features(df)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, shuffle=False
            )

            # Base models
            rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
            xgb = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, use_label_encoder=False, eval_metric='logloss')
            lgbm = LGBMClassifier(n_estimators=100, max_depth=4, learning_rate=0.1)

            # Scaled meta-learner (Logistic Regression)
            final_estimator = Pipeline([
                ('scaler', StandardScaler()),
                ('lr', LogisticRegression(max_iter=1000))
            ])

            # Stacked classifier
            stack = StackingClassifier(
                estimators=[
                    ('rf', rf),
                    ('xgb', xgb),
                    ('lgbm', lgbm)
                ],
                final_estimator=final_estimator,
                passthrough=True,
                cv=3
            )

            stack.fit(X_train, y_train)
            preds = stack.predict(X_test)
            acc = accuracy_score(y_test, preds)

            accuracies[ticker] = acc
            logger.info("Stacked Accuracy for %s: %.2f%%", ticker, acc * 100)

        except Exception as exc:
            logger.exception("Model failed for %s: %s", ticker, exc)

    return accuracies


'''import logging
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .indicators import add_indicators

logger = logging.getLogger(__name__)


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Generate features and labels for ML model.

    Label: 1 if next Close > current Close, else 0.
    Features: RSI, moving averages, lagged return, volume.
    """
    df = add_indicators(df.copy())

    # Avoid leakage by shifting return
    df["return_1d"] = df["Close"].pct_change().shift(1)
    df["next_close"] = df["Close"].shift(-1)
    df["label"] = (df["next_close"] > df["Close"]).astype(int)
    df.dropna(inplace=True)

    feature_cols = ["RSI_14", "MA_20", "MA_50", "return_1d", "Volume"]

    X = df[feature_cols]
    y = df["label"]

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return pd.DataFrame(X_scaled, index=X.index, columns=feature_cols), y


def train_evaluate(price_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """
    Train and evaluate Random Forest classifier for each ticker.

    Logs accuracy and prediction probabilities.

    Returns:
        Dict[str, float]: Mapping of ticker to accuracy.
    """
    accuracies = {}

    for ticker, df in price_data.items():
        try:
            X, y = prepare_features(df)

            if len(X) < 50:
                logger.warning("Skipping %s due to insufficient rows (%d)", ticker, len(X))
                continue

            # Chronological split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            preds = model.predict(X_test)
            probas = model.predict_proba(X_test)[:, 1]  # Confidence of class 1 (price going up)

            acc = accuracy_score(y_test, preds)
            accuracies[ticker] = acc

            logger.info("Accuracy for %s: %.2f%%", ticker, acc * 100)
            logger.debug("Example predicted probabilities for %s: %s", ticker, probas[:5])

        except Exception as exc:
            logger.exception("ML model failed for %s: %s", ticker, exc)

    return accuracies'''
