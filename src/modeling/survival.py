import pandas as pd
from sklearn.model_selection import train_test_split
from sksurv.nonparametric import kaplan_meier_estimator

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

# split into training/test x/y datasets
xtrain, xtest, ytrain, ytest = train_test_split(df["survival_time"], df[["conversion"]],
                                                train_size=0.8, random_state=43)


# estimate survival curve

