import pandas as pd
import numpy as np
from scipy.stats import uniform
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score, balanced_accuracy_score, f1_score

RANDOM_SEED = 999

# import data
X_train = pd.read_csv("data/clean/X_train.csv")
X_train = X_train.drop(["days_to_convert"], axis=1)

y_train = pd.read_csv("data/clean/y_train.csv")

X_test = pd.read_csv("data/clean/X_test.csv")
X_test = X_test.drop(["days_to_convert"], axis=1)

y_test = pd.read_csv("data/clean/y_test.csv")

# No information model (Predicts 0 for all records; due to imbalanced data, this should be highly accurate)
pred_0 = np.zeros(len(y_test))

# ol' logistic regression
model_1 = LogisticRegression(penalty='none')
model_1.fit(X_train, y_train)
pred_1 = model_1.predict_proba(X_test)

# Regularized regression (l2/Ridge)
model_2 = LogisticRegression(solver='liblinear', penalty="l2")
model_2_grid = {
    "C": uniform()
}

model_2_srch = RandomizedSearchCV(model_2, model_2_grid, scoring="neg_log_loss",
                                  cv=5, verbose=9, random_state=RANDOM_SEED)

model_2_srch.fit(X_train, y_train["conversion_ind"].values)
pred_2 = model_2_srch.predict_proba(X_test)

# Regularized regression (l1/Lasso)
model_3 = LogisticRegression(solver='liblinear', penalty="l1")
model_3_grid = {
    "C": uniform()
}

model_3_srch = RandomizedSearchCV(model_3, model_3_grid, scoring="neg_log_loss",
                                  cv=5, verbose=9, random_state=RANDOM_SEED)

model_3_srch.fit(X_train, y_train["conversion_ind"].values)
pred_3 = model_3_srch.predict_proba(X_test)


print(log_loss(y_test, pred_2[:, 1]))
