import pandas as pd
import numpy as np
from scipy.stats import uniform
import matplotlib.pyplot as plt
from sksurv.nonparametric import kaplan_meier_estimator
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sklearn.model_selection import RandomizedSearchCV
from lifelines import CoxPHFitter
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score, f1_score
import tqdm

# import data
X_train = pd.read_csv("data/clean/X_train.csv")
y_train = pd.read_csv("data/clean/y_train.csv")

X_test = pd.read_csv("data/clean/X_test.csv")
y_test = pd.read_csv("data/clean/y_test.csv")

X_train.loc[X_train["days_to_convert"] > 365, "days_to_convert"] = 365
X_train.loc[X_train["days_to_convert"] < 0, "days_to_convert"] = 0

y_train[X_train["days_to_convert"]>365] = 0
y_test[X_test["days_to_convert"]>365] = 0

# combine training data
train_combined = X_train.join(y_train)

# Unregularized survival model

cph = CoxPHFitter()
cph.fit(train_combined[['email_count', 'phone_call_count', 'walkin_count', 'CTOR',
                        'OR', 'days_to_convert', 'conversion_ind', 'ping_count_cut_med', 'ping_count_cut_high',
                        'sent_cut_med', 'sent_cut_high', 'sent_cut_very_high', 'open_cut_med', 'open_cut_high',
                        'origin_summary_Event Attendance', 'origin_summary_Event Registration',
                        'origin_summary_Inquiry Form', 'origin_summary_Source', 'origin_summary_Vendor Lead'
                        ]],
        duration_col="days_to_convert", event_col="conversion_ind")

# convert cumulative hazard function to probability to convert
predictions = 1-cph.predict_cumulative_hazard(X_test).T
predictions = np.subtract(predictions.T, predictions[365])

# calculate auc over time
auc_over_time = pd.DataFrame(data={"model": [],
                                   "days": [],
                                   "AUC": []})

for i in tqdm.tqdm(predictions.index[1:-1]):
    y_true = y_test[X_test["days_to_convert"]>i]
    y_pred = predictions.T[X_test["days_to_convert"]>i][i]

    value = log_loss(y_true, y_pred)
    auc_over_time.loc[len(auc_over_time.index)]=["Survival", i, value]


# this model performed less well than the static model, but this has no regularization
# TODO: Regularized survival model
cph2 = CoxPHFitter(penalizer=0.8)
cph2.fit(train_combined[['email_count', 'phone_call_count', 'walkin_count', 'CTOR',
                        'OR', 'days_to_convert', 'conversion_ind', 'ping_count_cut_med', 'ping_count_cut_high',
                        'sent_cut_med', 'sent_cut_high', 'sent_cut_very_high', 'open_cut_med', 'open_cut_high',
                        'origin_summary_Event Attendance', 'origin_summary_Event Registration',
                        'origin_summary_Inquiry Form', 'origin_summary_Source', 'origin_summary_Vendor Lead'
                        ]],
        duration_col="days_to_convert", event_col="conversion_ind")

predictions = 1-cph2.predict_cumulative_hazard(X_test).T
predictions = np.subtract(predictions.T, predictions[365])

for i in tqdm.tqdm(predictions.index[1:-1]):
    y_true = y_test[X_test["days_to_convert"]>i]
    y_pred = predictions.T[X_test["days_to_convert"]>i][i]

    value = log_loss(y_true, y_pred)
    auc_over_time.loc[len(auc_over_time.index)]=["Survival2", i, value]

auc_over_time.query("model=='Survival2'").plot(x="days", y="AUC")
