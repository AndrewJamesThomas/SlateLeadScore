from src.deployment.ModelDeployment import LeadScoreModel
from src.deployment.secrets import H, ID, PASSWORD


if __name__=="__main__":
    # import data & Model
    print("Importing Data & Model")
    model = LeadScoreModel(h=H, id=ID, years_min=1, years_max=0)
    model.load_model("src/deployment/LeadModel.pkl")

    # process data
    print("Processing Data")
    model.process_data(["person_id", "college_of_interest"])
    model.df.loc[:, ['origin_summary_Vendor Lead', 'origin_summary_2U Application', 'origin_summary_Event Attendance']] = 0

    # Run model
    print("Running Model")
    model.run_model()

    # Load model back to Slate
    model.deploy_to_slate(PASSWORD)
