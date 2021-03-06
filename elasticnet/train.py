import os
import warnings
import sys
from urllib.parse import urlparse

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
# from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet

import tensorflow as tf

import mlflow
import mlflow.sklearn
# import mlflow.tensorflow

import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def eval_metrics(actual, pred):
  rmse = np.sqrt(mean_squared_error(actual, pred))
  mae = mean_absolute_error(actual, pred)
  r2 = r2_score(actual, pred)
  return rmse, mae, r2


if __name__ == "__main__":
  warnings.filterwarnings("ignore")
  np.random.seed(40)

  (X_train, y_train), (X_test, y_test) = tf.keras.datasets.boston_housing.load_data(
    path="boston_housing.npz", test_split=0.2, seed=113)

  alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
  l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

  with mlflow.start_run():
      lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
      lr.fit(X_train, y_train)

      predicted_qualities = lr.predict(X_test)

      (rmse, mae, r2) = eval_metrics(y_test, predicted_qualities)

      print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
      print("  RMSE: %s" % rmse)
      print("  MAE: %s" % mae)
      print("  R2: %s" % r2)

      mlflow.log_param("alpha", alpha)
      mlflow.log_param("l1_ratio", l1_ratio)
      mlflow.log_metric("rmse", rmse)
      mlflow.log_metric("r2", r2)
      mlflow.log_metric("mae", mae)

      tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

      # Model registry does not work with file store
      if tracking_url_type_store != "file":

          # Register the model
          # There are other ways to use the Model Registry, which depends on the use case,
          # please refer to the doc for more information:
          # https://mlflow.org/docs/latest/model-registry.html#api-workflow
          mlflow.sklearn.log_model(lr, "model", registered_model_name="ElasticnetBoston")
      else:
          mlflow.sklearn.log_model(lr, "model")