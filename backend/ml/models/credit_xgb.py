import xgboost as xgb


def build_credit_model(params=None):
    defaults = {
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "max_depth": 4,
        "eta": 0.05,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
    }
    if params:
        defaults.update(params)
    return defaults


def train_credit_model(X_train, y_train, X_val, y_val, params=None, rounds=200):
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    model = xgb.train(
        build_credit_model(params),
        dtrain,
        num_boost_round=rounds,
        evals=[(dtrain, "train"), (dval, "val")],
        verbose_eval=False,
    )
    return model
