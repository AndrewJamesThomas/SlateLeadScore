import pandas as pd

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
# No null values, but only about 8% of leads convert into applicants.




'''
Processing Tasks:
    Fill missing colleges of interest with "unknown"
    Combine CAHSS colleges of interest
    Drop ELC, Law and LLI leads
    Convert Origin Date to datetime type
'''

