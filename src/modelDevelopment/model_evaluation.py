import pandas as pd
import seaborn as sns
from sklearn.metrics import log_loss
import tqdm

# read data
survival_noreg = pd.read_csv("data/predictions/survival_noreg.csv")
survival_reg = pd.read_csv("data/predictions/survival_withreg.csv")

static_noreg = pd.read_csv("data/predictions/static_regression_noreg.csv")
static_l1 = pd.read_csv("data/predictions/static_regression_l1.csv")
static_l2 = pd.read_csv("data/predictions/static_regression_l2.csv")

days_to_convert = pd.read_csv("data/clean/X_test.csv")

auc_over_time = pd.DataFrame(data={"model": [],
                                   "days": [],
                                   "AUC": []})


def add_evalutation_overtime(data, model_name, output=auc_over_time):
    # loop over all predictions
    for i in tqdm.tqdm(data.columns[1:-2]):
        # extract subquery at that time interval
        y_pred = data[days_to_convert["days_to_convert"] >= float(i)][str(float(i))]
        y_true = data[days_to_convert["days_to_convert"] >= float(i)]["conversion_ind"]

        # calculate log loss and append row
        value = log_loss(y_true, y_pred)
        auc_over_time.loc[len(auc_over_time.index)] = [model_name, i, value]
    print("All done")

# add data
add_evalutation_overtime(survival_noreg, "Survival Model WITHOUT Regularization")
add_evalutation_overtime(survival_reg, "Survival Model WITH Regularization")
add_evalutation_overtime(static_noreg, "Static Regression WITHOUT Regularization")
add_evalutation_overtime(static_l1, "L1 Static Regression")
add_evalutation_overtime(static_l2, "L2 Static Regression")

# plot lines

