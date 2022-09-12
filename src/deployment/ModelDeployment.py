import pandas as pd
import numpy as np
from datetime import date
import requests
from lifelines import CoxPHFitter
from joblib import dump, load
import paramiko
import math


class LeadScoreModel:
    def __init__(self, h, id, years_min, years_max):
        self.url = 'https://gradadmissions.du.edu/manage/query/run'
        self.df = self._query(h, id, years_min, years_max)
        self.model = None
        self.meta_data = None

    def _query(self, h, id, years_min, years_max):
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
            'h': h,
            'years_from': years_min,
            'years_to': years_max

        }
        req = requests.get(self.url, params)
        print(req)

        return pd.json_normalize(req.json(), record_path="row")

    def _fix_data_types(self):
        """
        converts incorrect data types to the correct data types
        """
        # Fix origin_date datatype
        self.df["origin_date"] = pd.to_datetime(self.df["origin_date"])

        # fix conversion date datatype
        self.df["conversion_date"] = pd.to_datetime(self.df["conversion_date"])

        # Calculate days until conversion
        self.df['days_to_convert'] = (self.df["conversion_date"] - self.df["origin_date"]).dt.days

        # impute missing conversion dates to difference between origin and current date
        self.df.loc[self.df["days_to_convert"].isna(), "days_to_convert"] = ((pd.to_datetime(date.today()) - self.df['origin_date']).dt.days + 1)

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

    def _cut_all_continuous_fields(self):
        """
        Cuts the sparsely populated ping fields into cateogrical fields
        """
        self.df["ping_count"] = ["ping_count_high" if i > 3
                                 else "ping_count_zero" if i == 0
                                 else "ping_count_low" for i in self.df['ping_count']]

        self.df["sent"] = ["sent_count_high" if i >= 23
                           else "sent_count_medium" if i >= 4 and i < 23
                           else "sent_count_low" if i >0 and i < 4
                           else "sent_count_zero" for i in self.df['sent']]

        self.df["open"] = ["open_count_high" if i >= 8
                           else "open_count_medium" if i >= 1 and i < 8
                           else "open_count_zero" for i in self.df['open']]

        self.df["click"] = ["click_count_high" if i >= 1
                            else "click_count_zero" for i in self.df['click']]

    def create_dummies(self, field):
        """
        Creates dummy variables from a given categorical field.
        :param field: str, categorical field that is being converted into dummy variables.
        :return: pd.Series
        """
        return self.df[field]\
            .pipe(pd.get_dummies, prefix=field)\
            .join(self.df)\
            .drop([field], axis=1)

    def _create_all_dummies(self):
        """
        Creates dummy variables for all categorical fields
        """
        self.df = self.create_dummies("ping_count", self.df)
        self.df = self.create_dummies("sent", self.df)
        self.df = self.create_dummies("open", self.df)
        self.df = self.create_dummies("click", self.df)
        self.df = self.create_dummies("origin_summary", self.df)

    def _select_key_columns(self):
        """
        Removes fields that are not used in modeling.
        """
        self.df = self.df[['email_count', 'phone_call_count', 'walkin_count', 'CTOR', 'OR', 'days_to_convert',
                           'conversion_ind', 'ping_count_cut_med', 'ping_count_cut_high', 'sent_cut_med',
                           'sent_cut_high', 'sent_cut_very_high', 'open_cut_med', 'open_cut_high',
                           'origin_summary_Event Attendance', 'origin_summary_Event Registration',
                           'origin_summary_Inquiry Form', 'origin_summary_Source', 'origin_summary_Vendor Lead',
                           "days_to_convert", "conversion_ind"]]

    def process_data(self, meta_fields):
        """
        Complets all nessecary processing steps at once.
        :param meta_fields: list, fields that should be removed from the modeling process but that should be retained for later use.
        """
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
        """
        Loads an pre-trained model saved at a specific location.
        :param path: str, location of a pre-trained model
        """
        self.model = load(path)

    def train_model(self):
        """
        Fits a model on cox-proportional hazard model with a regularization value of 0.8
        """
        self.model = CoxPHFitter(penalizer=0.8)
        self.model.fit(self.df, duration_col="days_to_convert", event_col="conversion_ind")

    def save_model(self, path):
        """
        Saves the trained model to a given path.
        :param path: str, location to save the model.
        """
        dump(self.model, path)

    def run_model(self):
        """
        Uses the trained model on the given data and produces the probability a record will convert within 1 year.
        """

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

    def deploy_to_slate(self, password, max_output_size=10000, username="dataanalyst@gradadmissions.du.edu"):
        """
        Deploys the predictions to Slate through an SFTP.
        :param password: str, sftp password
        :param path: max_output_size, the largest file that can be loaded to Slate. Larger files will be chunked into smaller files
        :param path: username, SFTP username.
        """
        # open sftp connection
        host = "ft.technolutions.net"
        todays_date = date.today().strftime("%Y%m%d")

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host, username=username, password=password)
        ftp_client = ssh_client.open_sftp()

        #chunk data
        number_of_chunks = math.ceil(self.meta_data.shape[0] / max_output_size)
        output_chunks = np.array_split(self.meta_data, number_of_chunks)

        print("Beginning Upload")
        for i, a in enumerate(output_chunks):
            # load dataframe to Slate SFTP
            # load to sftp
            path = f"/test/incoming/oge_modelling/lead_scoring/lead_scores_v3_{todays_date}_{i}.csv"
            print(f"Saving file {i} at location:\n{path}")
            with ftp_client.open(path, 'w',
                                 bufsize=32768) as f:
                f.write(a.to_csv(index=False))

        print("Upload Complete")
