<i><b>Note:</b> No personally identifying information or proprietary IP is included here. Care has been taken to comply with FERPA regulations and data security best practices. As such, no actual data or person-level results are available.</i>

# SlateLeadScore
The Lead Propensity Model indicates is intended to be used to prioritize outreach to prospective applicants. This means developing a predictive model that returns the probability a lead will convert (ie, start an application). All data will be extracted from Technolutions' Slate CRM and the model will likely rely on features such as email rates, website pings, and the time since the lead entered the funnel. While this should be a relatively straightforward model there are a number of key challenges to be aware of:

1) <strong>Lack of MLOPs infrastructure:</strong> Due to ongoing challenges, the university does not employ any MLOPs infrastructure and generally lacks a cohesive data plan. Therefore, we will be unable to rely on support from other departments such as IT and will not have access to the tools that would be traditionally be used to deploy a model such as this into production. Therefore, we will need to use more batch processes that occur locally and manually on a regular interval. 
2) <strong>Data Cleanliness:</strong> The manner in which lead data has been managed in Slate is painful. This will no doubt create issues throughout this processes. However, I believe that with enough data processing we should be able to produce a workable outcome. Ultimately, it is our suspicion that this problem is actually so easy that even our data management practices won't impede it's effectiveness to severly. 
3) <strong>Imbalanced data:</strong> While this is not technically a concern, the imbalances in this data should be noted. Roughly 93% of leads never convert, which creates heavy skewing that we will need to bare in mind going forward.

Broadly speaking, there are four critical phases to this project: extract the data from Slate, develop and deploy the model, set up a way to load data back into slate, and continue to monitor the process moving forward.

## Data Extraction
We can leveage Slate's exisiting webservices tools to easily and securly extract data from the database. Note that we are not using Slate's "query" tools because that does not offer us the flexability needed for this project. Rather, we will a) write custom SQL to access the data needed b) set up a query in Slate using the "custom SQL" query base that will allow us to expose the results of the query using web services and c) use python to request this data on demand through an API call. For posteriety, the SQL used for this underlying query will be included in this repo, but note that this code is never called by any code here. Rather, that code is copied into Slate and ran as a "Slate query". 

Note that, due to FERPA requirements, general data privacy common sense, and a variety of other reasons, raw data is not included in this repo.

## Predictive Modeling
The reality of this project is that, while most leads never start an application, the ones who do signal their intention fairly loudly. This means that building a predictive model should be realively easy. 

There are three key components of this model 1) Origin source (such as an inquiry form, list buy, event, etc.) 2) Online Activity (such as email activity, website pings, phone calls, etc.) 3) Time since Creating (We know that most leads convert in the first couple days, but the likelihood drops off signficantly after that). The first two components are extremely straightforward, but that last one is more complicated. Modelling that relationship will likely require somekind of surival-aware or sequence model.

There are two main concerns with using a propensity model in this way:
a) Individuals may want to include their own variables with their own wieghts. This may seem like an odd request, but it is likely to occur. If this turns out to be an issue we can simply build an alternative "points based" system that can accomadate this request.
b) Due to the imbalances in this data, most scores are likely to be extremely small. It may be problematic if most records have a score between 0-3%. Therfore, we should consider alternative approaches, such as ranking these scores so we can identify the "most likely to convert" leads or we could group leads into "unlikely to convert", "may convert", and "likely to convert" buckets.

## Deployment
We do not have access to normal MLOPs tools such as those found on AWS or Azure. Furthermore, IT has generally been retisent to support this kind of project in the past. Therefore we will have to run the model locally on a regular basis. To do this we will simply pull the data through the API, process it and run the model, then load the data back on to the Slate SFTP so that the batch tools can complete the upload automatically. It is likely possible to use the API to bypass the SFTP, but for now this is the easiest path forward. 

One major complication is that the size of each file has to be relatively small. There is no hard cutoff on filesize, but if it is too large then it is likely to fail sporadically. The easy solution to this is to a) score only "recent leads" not the entire database and b) break each file into smaller chunks that are more likely to load sucessfully.

Moving forward we will need to run this process as part of the routine weekly tasks. However, we should push to automate this process when possible.
