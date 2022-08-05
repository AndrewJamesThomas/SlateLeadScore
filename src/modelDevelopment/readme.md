# Model Development
The scripts in this directory are used to process our data and development the final model. This will eventually be used as the basis of our "modelDeployment" scripts.
Only a small fraction of the code here will be used in deployment, but we have included this code here for posterity. 

The plan is to test four different modeling approaches and then select the option that performs best. These are approaches include static models, a survival model, a Markov Chain and a RNN model.
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

## Evaluation
While the static models perform best at t=0, but overtime the regularized surival model outperforms the other options
https://github.com/thomasandr/SlateLeadScore/blob/main/assets/model_performance.png
