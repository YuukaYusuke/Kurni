from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

MODEL_NAMES = {
    "dt": "Decision Tree",
    "nb": "Naive Bayes",
}

PARAM_GRIDS = {
    "dt": {
        "max_depth": [6, 8, 10, 12, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "criterion": ["gini", "entropy"],
    },
    "nb": {
        "var_smoothing": [1e-10, 1e-9, 1e-8, 1e-7, 1e-6],
    },
}


def _evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
        "confusion": confusion_matrix(y_test, y_pred).tolist(),
        "roc_curve": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
    }


def _train_single_model(key, estimator, X_train, y_train, X_test, y_test, cv):
    grid_search = GridSearchCV(
        estimator,
        PARAM_GRIDS[key],
        cv=cv,
        scoring="f1",
        n_jobs=-1,
        refit=True,
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    cv_accuracy = cross_val_score(best_model, X_train, y_train, cv=cv, scoring="accuracy")
    cv_f1 = cross_val_score(best_model, X_train, y_train, cv=cv, scoring="f1")
    cv_roc = cross_val_score(best_model, X_train, y_train, cv=cv, scoring="roc_auc")

    eval_metrics = _evaluate_model(best_model, X_test, y_test)

    top_results = sorted(
        grid_search.cv_results_["mean_test_score"],
        reverse=True,
    )[:5]

    return best_model, {
        "name": MODEL_NAMES[key],
        "model": best_model,
        "best_params": grid_search.best_params_,
        "best_cv_f1": float(grid_search.best_score_),
        "cv_accuracy_mean": float(cv_accuracy.mean()),
        "cv_accuracy_std": float(cv_accuracy.std()),
        "cv_f1_mean": float(cv_f1.mean()),
        "cv_f1_std": float(cv_f1.std()),
        "cv_roc_auc_mean": float(cv_roc.mean()),
        "cv_roc_auc_std": float(cv_roc.std()),
        "top_cv_scores": [float(s) for s in top_results],
        "n_combinations": int(len(grid_search.cv_results_["params"])),
        **eval_metrics,
    }


def train_models(X, y):
    """Pipeline ML: split data → GridSearchCV → cross-validation → evaluasi test."""
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.2, random_state=42, stratify=y_temp
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    estimators = {
        "dt": DecisionTreeClassifier(random_state=42, class_weight="balanced"),
        "nb": GaussianNB(),
    }

    metrics = {
        "split": {
            "train": len(X_train),
            "val": len(X_val),
            "test": len(X_test),
            "total": len(X),
            "train_pct": round(len(X_train) / len(X) * 100, 1),
            "val_pct": round(len(X_val) / len(X) * 100, 1),
            "test_pct": round(len(X_test) / len(X) * 100, 1),
        },
        "cv_folds": 5,
        "scoring": "f1",
    }

    models = {}
    for key, estimator in estimators.items():
        model, result = _train_single_model(
            key, estimator, X_train, y_train, X_test, y_test, cv
        )
        models[key] = model
        result["train_size"] = len(X_train)
        result["val_size"] = len(X_val)
        result["test_size"] = len(X_test)
        result["val_metrics"] = _evaluate_model(model, X_val, y_val)
        metrics[key] = result

    best_key = max(["dt", "nb"], key=lambda k: metrics[k]["f1"])
    metrics["best_model"] = MODEL_NAMES[best_key]
    metrics["best_model_key"] = best_key

    return models["dt"], models["nb"], metrics, list(X.columns), models
