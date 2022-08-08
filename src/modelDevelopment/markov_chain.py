import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
import tqdm

RANDOM_SEED = 999

# import data
X_train = pd.read_csv("data/clean/X_train.csv")
y_train = pd.read_csv("data/clean/y_train.csv")
train = pd.concat([X_train, y_train], axis=1)
train.loc[train["days_to_convert"] > 365, "days_to_convert"] = 365
train.loc[train["days_to_convert"] < 0, "days_to_convert"] = 0

X_test = pd.read_csv("data/clean/X_test.csv")
y_test = pd.read_csv("data/clean/y_test.csv")
test = pd.concat([X_test, y_test], axis=1)
test.loc[test["days_to_convert"] > 365, "days_to_convert"] = 365
test.loc[test["days_to_convert"] < 0, "days_to_convert"] = 0


# create chain
class BuildMarkovModel:
    def __init__(self, training, testing):
        self.training = training
        self.testing = testing
        self.chain = {}

    def _create_subset(self, days):
        training_subset = self.training[self.training["days_to_convert"] >= days]
        testing_subset = self.testing[self.testing["days_to_convert"] >= days]

        self.chain[days] = {
            "train": training_subset,
            "test": testing_subset
        }

    def build_chain(self, max_days):
        for i in tqdm.tqdm(range(max_days)):
            self._create_subset(i)

    def build_models(self):
        # add a new model to each state, giving the probability of success
        if len(self.chain.keys()) == 0:
            print("Please Build Chain First (use self.build_chain)")
            return -1

        for s in tqdm.tqdm(self.chain.keys()):
            # build model
            x = self.chain[s]['train'].drop(["days_to_convert", "conversion_ind"], axis=1)
            y = self.chain[s]["train"]["conversion_ind"]
            model = LogisticRegression()
            model.fit(x, y)

            # add model to the chain
            self.chain[s]["model"] = model

            # test the model
            x_test_chain = self.chain[s]['test'].drop(["days_to_convert", "conversion_ind"], axis=1)
            y_test_chain = self.chain[s]['test']["conversion_ind"]

            proba = model.predict_proba(x_test_chain)[:,1]
            log_loss_value = log_loss(y_test_chain, proba)
            auc_value = roc_auc_score(y_test_chain, proba)

            self.chain[s]["log_loss"] = log_loss_value
            self.chain[s]["auc"] = auc_value

    def get_evaluation_numbers(self):
        # AUC
        auc_over_time = pd.DataFrame(data={"model": [],
                                           "days": [],
                                           "AUC": []})
        for r in self.chain:
            auc_over_time.loc[len(auc_over_time)] = ["MarkovModel", r, self.chain[r]["auc"]]

        # Log Loss
        log_loss_overtime = pd.DataFrame(data={"model": [],
                                               "days": [],
                                               "Log Loss": []})
        for r in self.chain:
            log_loss_overtime.loc[len(log_loss_overtime)] = ["MarkovModel", r, self.chain[r]["log_loss"]]

        return auc_over_time, log_loss_overtime


if __name__=="__main__":
    MarkovChain = BuildMarkovModel(train, test)
    MarkovChain.build_chain(365)
    MarkovChain.build_models()
    auc_values, log_loss_values = MarkovChain.get_evaluation_numbers()

    auc_values.to_csv("data/predictions/MC_AUC.csv", index=False)
    log_loss_values.to_csv("data/predictions/MC_LOG_LOSS.csv", index=False)
