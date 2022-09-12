# Model Development
The scripts in this directory are used to process our data and development the final model. This will eventually be used as the basis of our "modelDeployment" scripts.
Only a small fraction of the code here will be used in deployment, but we have included this code here for posterity. 

The plan is to test three different modeling approaches and then select the option that performs best. These are approaches include static models, a survival model and a Markov Chain model.
The motivation behind these approaches is that they all handle the "days to convert" field in different ways. This field represents the number of days between when a lead enters the funnel 
and when they exist the funnel. If they do convert, then this value is less than 365, if they never convert (or take longer than a year to convert) then the value is exactly 365.
We know from our EDA that if this field is used correctly then it will likely be highly predictive. However, if also poses a significant data leakage risk.

## Static Model
What we are calling "the static model approach" is the simpilest option and acts as our model baseline. It deals with the "days to convert" problem, by dropping that variable and accepting
that this will result in a hit to model accuracy. While this is not desirable, it may not matter if these models perform sufficiently well.

More specifically, we are three seperate models: a simple logistic regression with no regularization, L1 regularized logistic regression and an L2 regularized regression. 
One could argue that these are bassically just the same model and that we should include some additional options such as RandomForest or GBM, but becuase this is baseline model, we will stick with the basics.

The hyperparameters were tuned using a 5-fold cross validation random grid search process, minimizing the model log loss. A more robust performance analysis will be presented
later, but at first blush we see three conlcusions: 1) The Ridge model does marginally better than the other two models (Log Loss: 0.176) 2) There is a signficant boost in performance
of the no information model (which predicts all records will not convert), however 3) The percision/recall/F1 scores are all pretty low (F1 Score: 0.42)

## Survival Model
The Survival model uses fits a simple Cox Porportional Hazard model to determine the likelihood of survival to t=365. We use this PDF to determine the probability of not surviving (ie, the likelihood of converting). This model is theoretically preferable to the static models because it allows the probability of a conversion to decrease over time, which we know intuitively to be true, and as we see in our model evaluation, this turns out to be true. While the surival model performs similiarly to the static models at t=0, it's relative performance improves overtime and begins to vastly outperform the static models at the year goes on. 

## Markov Model
The Markov Model takes a similiar approach to the survival model. Each day is treated as a "state" and each applicant has a probablity of transitioning to either the next day or to a "conversion state". This is a relatively simple approach that essesntially just consists of subsetting the training data to remove applicants who converted prior to the given state then training 365 different models to provide the transition probability for each state. It is essentially just a more non-parametric version of the survival model.

The model returns similiar results to the survival models in that the performance starts out similiar to the static approach but begins to improve over time. However, it does underperform the survival model later in the years, making it the less preferable approach.

## Evaluation
Determining the best modeling approach depends on where in the timeline we look. We see that from day 0 to about day 50 the markov model performs marginally better, than the regularized survival model, but after that cutoff point the survival approach starts win-out. At no point would it make sense to pursue the static models or an unregularized survival model.

Overall, it appears that the survival model outperforms the markov model more late in the year than the markov model outperforms early in the year. Therefore, we will choose to move forward with only the survival model.

!['https://github.com/thomasandr/SlateLeadScore/blob/main/assets/model_performance3.png'](https://github.com/thomasandr/SlateLeadScore/blob/main/assets/model_performance3.png)
