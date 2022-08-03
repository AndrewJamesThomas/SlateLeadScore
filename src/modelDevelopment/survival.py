import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sksurv.nonparametric import kaplan_meier_estimator
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, balanced_accuracy_score
from sksurv.metrics import cumulative_dynamic_auc

# setup data
df = pd.read_csv("data/proofOfConcept.csv")
# check missing values
df.isna().mean() # all good

# fix data types
df[['origin_date', "conversion_date"]] = df[['origin_date', "conversion_date"]].apply(pd.to_datetime)

# calculate days between origin date and conversion date
df["survival_time"] = (df["conversion_date"] - df["origin_date"]).dt.days
# if a record has no conversion, imput with 1 year
df["survival_time"] = df["survival_time"].fillna(365)
# fill outlies with 365
df.loc[df["survival_time"]>365, "survival_time"] = 365
df.loc[df["survival_time"]==365, 'conversion'] = 0

# switch the conversions
df = df[df["survival_time"]>=0]

# split into training/test x/y datasets
xtrain, xtest, ytrain, ytest = train_test_split(df["survival_time"], df[["conversion"]],
                                                train_size=0.8, random_state=43)


time, survival_prob = kaplan_meier_estimator(ytrain==1, xtrain)

plt.step(time, survival_prob - min(survival_prob))
plt.show()

# Evaluate
auc_train = [(a, b) for a, b in pd.concat([ytrain==1, xtrain], axis=1).values]
auc_test = [(a, b) for a, b in pd.concat([ytest==1, xtest], axis=1).values]
times = np.arange(0, 350, 1)

auc, mean_auc = cumulative_dynamic_auc(np.array(auc_train, dtype=[('Status', '?'), ('Survival_in_days', '<f8')]),
                                       np.array(auc_test, dtype=[('Status', '?'), ('Survival_in_days', '<f8')]),
                                       survival_prob, times)