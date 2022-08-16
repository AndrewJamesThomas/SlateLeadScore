import pandas as pd
import numpy as np
from datetime import date, timedelta
import requests
from lifelines import CoxPHFitter
from joblib import dump, load


class GetSlateData:
    def __init__(self, h, id):
        self.url = 'https://gradadmissions.du.edu/manage/query/run'
        self.df = self._query(h, id)
        self.model = None
        self.meta_data = None

    def _query(self, h, id):
        """
        Simply use the parameters from the webservices URL and the results of that query will be returned as a pandas
        dataframe.
        :param h: str, The value labels "h" in the webservices url (the last parameter)
        :param id: str, The query id
        :return: pd.DataFrame
        """
        params = {
            'id': id,
            'cmd': 'service',
            'output': 'json',
            'h': h
        }
        req = requests.get(self.url, params)
        return pd.json_normalize(req.json(), record_path="row")

    def _fix_data_types(self):
        """
        converts incorrect data types to the correct data types
        """
        # Fix origin_date datatype
        self.df["origin_date"] = pd.to_datetime(self.df["origin_date"])
        # Remove leads from the last year
        df = self.df[self.df["origin_date"] < (date.today() - pd.DateOffset(years=1))]

        # fix conversion date datatype
        self.df["conversion_date"] = pd.to_datetime(self.df["conversion_date"])

        # impute missing conversion dates to one year from the origin date
        self.df.loc[self.df["conversion_date"].isna(), "conversion_date"] = self.df["origin_date"] + timedelta(days=365)

        # Calculate days until conversion
        self.df['days_to_convert'] = (self.df["conversion_date"] - self.df["origin_date"]).dt.days

        # message fields
        int_fields = ["sent", "open", "click", "ping_count", "apt_count", "chat_count", "email_count",
                      "phone_call_count", "walkin_count", "conversion_ind"]
        self.df[int_fields] = self.df[int_fields].astype(int)


    def _extract_inquiry_forms(self):
        """
        Convert any origin with 'inquiry' in the summary to 'Inquiry Form'
        """
        self.df.loc[self.df["origin_summary"].str.contains("Inquiry"), "origin_summary"] = "Inquiry Form"

    def _get_message_rates(self):
        """
        Calculate Open and Click Thru Open Rates
        """
        # create open rates
        self.df["OR"] = self.df["open"] / self.df["sent"]
        self.df["OR"] = self.df["OR"].fillna(0)

        # Create CTOR
        self.df["CTOR"] = self.df["click"] / self.df["open"]
        self.df["CTOR"] = self.df["CTOR"].fillna(0)

    @staticmethod
    def cut_continuous_fields(field, cut_count, labels, data):
        new_field_name = field + "_cut"
        data[new_field_name] = pd.qcut(data[field], cut_count, duplicates='drop', labels=labels)
        data = data.drop([field], axis=1)
        return data

    def _cut_all_continuous_fields(self):
        self.df = self.cut_continuous_fields("ping_count", 15, ["low", "med", "high"], self.df)
        self.df = self.cut_continuous_fields("sent", 4, ["low", "med", "high", "very_high"], self.df)
        self.df = self.cut_continuous_fields("open", 4, ["low", "med", "high"], self.df)

    @staticmethod
    def create_dummies(field, data):
        return data[field]\
            .pipe(pd.get_dummies, prefix=field)\
            .join(data)\
            .drop([field], axis=1)

    def _create_all_dummies(self):
        self.df = self.create_dummies("ping_count_cut", self.df)
        self.df = self.create_dummies("sent_cut", self.df)
        self.df = self.create_dummies("open_cut", self.df)
        self.df = self.create_dummies("origin_summary", self.df)

    def _select_key_columns(self):
        self.df = self.df[['email_count', 'phone_call_count', 'walkin_count', 'CTOR', 'OR', 'days_to_convert',
                           'conversion_ind', 'ping_count_cut_med', 'ping_count_cut_high', 'sent_cut_med',
                           'sent_cut_high', 'sent_cut_very_high', 'open_cut_med', 'open_cut_high',
                           'origin_summary_Event Attendance', 'origin_summary_Event Registration',
                           'origin_summary_Inquiry Form', 'origin_summary_Source', 'origin_summary_Vendor Lead',
                           "days_to_convert", "conversion_ind"]]

    def process_data(self, meta_fields):
        self._fix_data_types()
        self._extract_inquiry_forms()
        self._get_message_rates()
        self._cut_all_continuous_fields()
        self._create_all_dummies()
        self.df = self.df.drop(["chat_count", "walkin_count"], axis=1)

        self.df.loc[self.df["days_to_convert"] > 365, "days_to_convert"] = 365
        self.df.loc[self.df["days_to_convert"] < 0, "days_to_convert"] = 0

        self.meta_data = self.df[meta_fields + ["days_to_convert"]]
        self.df = self.df.drop(meta_fields, axis=1)
        self.df = self.df.drop(["origin_date", "conversion_date"], axis=1)

    def load_model(self, path):
        self.model = load(path)

    def train_model(self):
        self.model = CoxPHFitter(penalizer=0.8)
        self.model.fit(self.df, duration_col="days_to_convert", event_col="conversion_ind")

    def save_model(self, path):
        dump(self.model, path)

    def run_model(self):
        # convert cumulative hazard function to probability to convert
        predictions = 1 - self.model.predict_cumulative_hazard(self.df).T
        predictions = np.subtract(predictions.T, predictions[365])
        predictions = predictions.T
        predictions = predictions.join(self.meta_data["person_id"])
        predictions = pd.melt(predictions, id_vars="person_id", var_name="days", value_name="proba")
        self.meta_data = self.meta_data.merge(predictions,
                                              left_on=["person_id", "days_to_convert"],
                                              right_on=["person_id", "days"])
        return predictions


if __name__ == "__main__":
    H = "e3fe870e-f998-454a-a77b-099675f3daa0"
    ID = "391e2b7e-a6d1-4fdc-9f0c-976189b74e45"

    model = GetSlateData(h=H, id=ID)
    model.process_data(["person_id", "college_of_interest"])
    model.train_model()
    predictions = model.run_model()

#    output = model.meta_data
