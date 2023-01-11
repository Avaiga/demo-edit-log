from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as MSE
import xgboost as xg
import pandas as pd
import numpy as np


# Drop Columns Function
def drop_cols(in_data, cols):
    out_data = in_data.drop(cols, axis=1)
    return out_data


# Create Categories Function
def create_categories(in_data):
    out_data = in_data.copy()
    out_data = pd.get_dummies(out_data, drop_first=True)
    return out_data


# Split Data Function
def split_data(in_data):
    X = in_data.drop("price", axis=1)
    y = in_data["price"]
    train_X, test_X, train_y, test_y = train_test_split(
        X, y, test_size=0.3, random_state=123
    )
    return (train_X, test_X, train_y, test_y)


def train_xgb(in_data):
    print("Training XGB")
    train_X, test_X, train_y, test_y = in_data
    xgb_r = xg.XGBRegressor(objective="reg:squarederror",
                            n_estimators=10, seed=123)
    # Fitting the model
    xgb_r.fit(train_X, train_y)
    return xgb_r


def predict_m(model, data):
    train_X, test_X, train_y, test_y = data
    # Predict the model
    pred = model.predict(test_X)
    # RMSE Computation
    rmse = np.sqrt(MSE(test_y, pred))
    print("RMSE : % f" % (rmse))
    out_data = pd.DataFrame(pred)
    return out_data


def train_rf(in_data):
    print("Training RF")
    train_X, test_X, train_y, test_y = in_data
    rf_r = RandomForestRegressor(n_estimators=30)
    rf_r.fit(train_X, train_y)
    return rf_r


def create_output_data(split_data, xgb_preds, rf_preds):
    train_X, test_X, train_y, test_y = split_data
    out_data = pd.concat([test_y.reset_index(drop=True),
                         xgb_preds, rf_preds], axis=1)
    out_data.columns = ["Test Y", "XGB Predictions",
                        "Random Forest Predictions"]
    out_data["XGB Predictions"] = out_data["XGB Predictions"].apply(
        lambda d: round(d, 1)
    )
    out_data["XGB Predictions"] = out_data["XGB Predictions"].apply(
        lambda d: round(d, 1)
    )

    return out_data
