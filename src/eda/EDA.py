# Note: In order to comply with FERPA and University Policy aggregates and raw data will not be made available here.
import pandas as pd
pd.set_option('display.max_rows', 500)

df = pd.read_csv("data/lead_scoring_3_years.csv")

# check columns and shape
df.shape
df.info()
''' Thoughts:
     Data types are wrong for origin_date and conversion_date
     there are two columns for "sent"
     We will need to handle null values for several columns
'''

# person_id
df["person_id"].head()
# Looks fine

# College of Interest
df["college_of_interest"].head()
df["college_of_interest"].isna().mean()
# about 17% of records are not attached to a college. Great work everyone.

df.groupby('college_of_interest').size().sort_values(ascending=False)
'''most records belong to DCB, JKSIS, UCOL, MCE, NSM and RESECS
   CAHSS also has a lot, but they are split between their various names. These will need to be aggregated.
   There are a lot of leads for ELC and Law, LLI and a few for "Unkown"
   Odly there are not many for GSSW or GSPP
'''

# Origin Date
df["origin_date"]
# need to convert date type to datetime
df["origin_date"].isna().mean()
# No missing origin dates, which is merciful
df.groupby("origin_date").size().plot()
# initial ploting shows some random spikes (likely data loads) and seasonality

# conversion_ind
df['conversion_ind'].head()
df["conversion_ind"].isna().mean()
df["conversion_ind"].describe()
# No null values, but only about 8% of leads convert into applicants. Which is very skewed
# this column looks good otherwise.

# origin_summary
df["origin_summary"].head()
df["origin_summary"].isna().mean()
# There is on missing data in this column, great!
df.groupby('origin_summary').size().sort_values(ascending=False)/len(df)
# These origin summaries are pretty chaotic. Each inquiry form has it's own origin (ie, GSSP Inquiry, DCB Inquiry, etc)
# Other origins are pretty non-descript (ie, "source", "Ad-Hoc Data Load", etc.)
# About 70% of leads are "source", "Ad-Hoc Data Load", or "Vendor Lead". Most of the rest are inquiries.
# will be interesting to see cross tabs with memo, etc.
df.groupby("origin_summary").agg(["mean", 'size'])["conversion_ind"].sort_values("size")

# Origin Memo
df["origin_memo"].head()
df["origin_memo"].isna().mean()
# no missing values
round((df.groupby('origin_memo').size().sort_values(ascending=False)/len(df))*100, 0)
# There are 315 different memos.
# these could perhaps be aggreagted (ie, GRE Search, etc.)
# Some just make no sense though (ex, one is just "University College")

df.groupby("origin_memo").agg(["mean", 'size'])["conversion_ind"].sort_values("size")
# Looks like list buys get like ~2%; # RFI and inquiry fors get like ~20%

# Sent
df["sent"].head()
df["sent"].isna().mean()
# About 18% of records are null
df["sent"].describe()
# Some heavy outliers
# Mean of 18, median of 10

# There is a data leakage problem here. If someone never applies then they just keep getting emails
# so more emails==never converted. Easy fix, but needs to happen on the SQL side
df[["sent", "conversion_ind"]].corr()
# Some negative correlation between emails sent and conversions. This is expected given data leakage.

'''
Processing Tasks:
    Fill missing colleges of interest with "unknown"
    Combine CAHSS colleges of interest
    Drop ELC, Law and LLI leads
    Convert Origin Date to datetime type
    Combine Inquiry forms into single origin
    Combine major "origin_memos" together
    Imput Null Values for sent
    Fix data leakage issue in SQL
'''

