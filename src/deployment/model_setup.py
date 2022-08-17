from src.deployment.ModelDeployment import LeadScoreModel
from src.deployment.secrets import H, ID

if __name__=="__main__":
    #import data
    model = LeadScoreModel(h=H, id=ID, years_min=5, years_max=4)
    model.process_data(["person_id", "college_of_interest"])
    model.train_model()
    model.save_model("src/deployment/LeadModel.pkl")
