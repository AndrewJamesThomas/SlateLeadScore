import pandas as pd
from datetime import timedelta
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/raw/lead_scoring_4_years.csv")

# --------- College of Interest
# Fill in missing College of Interest with "Unknown"
df["college_of_interest"] = df["college_of_interest"].fillna("Unknown College")

# group CAHSS units together
cahss_units = ['Lamont School of Music', 'Arts and Humanities Division', 'Social Sciences Division']
df\
    .loc[df["college_of_interest"].isin(cahss_units), "college_of_interest"] \
    = 'College of Arts, Humanities and Social Sciences'

# drop units that we no longer collect data for
colleges_to_drop = ['Latino Leadership Institute', 'Graduate Tax Program', 'Sturm College of Law',
                    'English Language Center']
df = df.loc[~df["college_of_interest"].isin(colleges_to_drop)]

# --------- Origin/Conversion Dates
# Fix origin_date datatype
df["origin_date"] = pd.to_datetime(df["origin_date"])

# fix conversion date datatype
df["conversion_date"] = pd.to_datetime(df["conversion_date"])

# impute missing conversion dates to one year from the origin date
df.loc[df["conversion_date"].isna(), "conversion_date"] = df["origin_date"] + timedelta(days=365)

# Calculate days until conversion
df['days_to_convert'] = (df["conversion_date"] - df["origin_date"]).dt.days

# --------- origin_summary
df.loc[df["origin_summary"].str.contains("Inquiry"), "origin_summary"] = "Inquiry Form"

# --------- sent/open/click/Ping
# create open rates
df["OR"] = df["open"]/df["sent"]
df["OR"] = df["OR"].fillna(0)

# Create CTOR
df["CTOR"] = df["click"]/df["open"]
df["CTOR"] = df["CTOR"].fillna(0)


# handle outliers by binning fields into quartiles
def cut_continuous_fields(field, cut_count, labels, data):
    new_field_name = field + "_cut"
    data[new_field_name] = pd.qcut(data[field], cut_count, duplicates='drop', labels=labels)
    data = data.drop([field], axis=1)
    return data


df = cut_continuous_fields("ping_count", 15, ["low", "med", "high"], df)
df = cut_continuous_fields("sent", 4, ["low", "med", "high", "very_high"], df)
df = cut_continuous_fields("open", 3, ["low", "med", "high"], df)


# --------- Create dummy fields
def create_dummies(field, data=df):
    return data[field]\
        .pipe(pd.get_dummies, prefix=field)\
        .join(data)\
        .drop([field], axis=1)

df = create_dummies("ping_count_cut", df)
df = create_dummies("sent_cut", df)
df = create_dummies("open_cut", df)
df = create_dummies("origin_summary", df)

# --------- finalize and save cleaned data
df = df[['person_id', 'origin_date', 'conversion_date', 'college_of_interest', 'conversion_ind',
    'origin_summary_Ad-Hoc Data Load', 'origin_summary_Event Attendance', 'origin_summary_Event Registration',
    'origin_summary_Inquiry Form', 'origin_summary_Source', 'origin_summary_Vendor Lead', 'open_cut_low',
    'open_cut_med', 'open_cut_high', 'sent_cut_low', 'sent_cut_med', 'sent_cut_high', 'sent_cut_very_high',
    'ping_count_cut_low', 'ping_count_cut_med', 'ping_count_cut_high', 'click', 'apt_count', 'chat_count',
    'email_count', 'phone_call_count', 'walkin_count', 'OR', 'CTOR', 'days_to_convert']]

# split into training/testing/meta datasets
RANDOM_SEED = 999

y = df["conversion_ind"]

non_predictors = ["person_id", "origin_date", "conversion_date", "college_of_interest", "conversion_ind"]
X = df.drop(non_predictors, axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED)

# save data
df.to_csv("data/clean/full_lead_data.csv", index=False)

X_train.to_csv("data/clean/X_train.csv", index=False)
y_train.to_csv("data/clean/y_train.csv", index=False)

X_test.to_csv("data/clean/X_test.csv", index=False)
y_test.to_csv("data/clean/y_test.csv", index=False)
