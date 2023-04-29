import argparse
import datetime

from Services.WorkItemService import WorkItemService
from Services.MonteCarloService import MonteCarloService

from Classes.Prediction import Prediction

parser = argparse.ArgumentParser()
parser.add_argument("--PersonalAccessToken")
parser.add_argument("--OrganizationUrl")
parser.add_argument("--ReleaseTag")
parser.add_argument("--TargetDate")
parser.add_argument("--GoalTag")
parser.add_argument("--IterationLength")

args = parser.parse_args()

work_item_service = WorkItemService(args.OrganizationUrl, args.PersonalAccessToken)

release_tag = args.ReleaseTag
goal_tag = args.GoalTag
target_date = None
if args.TargetDate:
    target_date = datetime.datetime.strptime(args.TargetDate, "%d.%m.%Y").date()

iteration_length = None
if args.IterationLength:
    iteration_length =  int(args.IterationLength)

                # Work Item Types, Enable Prediction, History in Days, Done States, Area Paths
predictions = [ Prediction(["Epic"], False, 180, ["Closed", "Resolved"], ["MyProduct\MyAreaPath"]),
                Prediction(["Feature"], False, 120, ["Closed","Resolved"], []),
                Prediction(["User Story", "Bug"], True, 90, ["Closed"], ["MyProduct\MyAreaPath"])]

def get_remaining_items_by_tag_and_type(work_item_types, tag):    
    print("Fetching items linked to Tag {0}:".format(tag))
    work_items = work_item_service.get_open_items_by_tag(tag)
    
    remaining_items = []   
    
    for item in work_items:
        if item.type in work_item_types:
          remaining_items.append(item)
          print("{0} - {1} - {2} - {3} - {4} - {5} - {6} - {7}".format(item.id, item.type, item.title, item.state, item.tags, item.boardColumn, item.closedDate, item.area_path))
    
    remaining_items = len(remaining_items)
    
    print("{0} Items remaining".format(remaining_items))
    return remaining_items

def get_closed_items_history(prediction):
    start_date = datetime.datetime.now() - datetime.timedelta(prediction.relevant_history_in_days)
    
    work_items = work_item_service.get_items_by_area_paths(prediction.work_item_types, prediction.area_paths, [], start_date.strftime("%m-%d-%Y"))
    closed_items_history = monte_carlo_service.create_closed_items_history(work_items)
    return closed_items_history

def add_forecast_to_prediction(prediction, how_many_50, how_many_85, how_many_95, when_50, when_85, when_95, target_date, target_date_likelyhood):
    prediction.how_many_50 = how_many_50
    prediction.how_many_85 = how_many_85
    prediction.how_many_95 = how_many_95
    
    prediction.when_50 = when_50
    prediction.when_85 = when_85
    prediction.when_95 = when_95
    
    prediction.target_date_likelyhood = target_date_likelyhood
    prediction.target_date = target_date

print("================================================================")
print("Starting Monte Carlo Simulation...")
print("================================================================")  
print("Parameters:")
print("OrganizationUrl: {0}".format(args.OrganizationUrl))
print("ReleaseTag: {0}".format(args.ReleaseTag))
print("TargetDate: {0}".format(args.TargetDate))
print("GoalTag: {0}".format(args.GoalTag))
print("IterationLength: {0}".format(args.IterationLength))
print("----------------------------------------------------------------")
   
for prediction in predictions.copy():        
    if prediction.run_prediction == False:            
        print("Predictions for {0} disabled - skipping".format(prediction.work_item_types))
        continue

    monte_carlo_service = MonteCarloService(prediction)

    print("Running Prediction for work item type '{0}' and Area Path '{1}'".format(prediction.work_item_types, prediction.area_paths))    
    
    closed_items_history = get_closed_items_history(prediction)        
    if len(closed_items_history) < 1:
        print("No closed items - skipping prediction")
        continue
    
    ## Run How Many Predictions via Monte Carlo Simulation - only possible if we have a target date set
    predictions_howmany_50 = predictions_howmany_85 = predictions_howmany_95 = 0
    if target_date:
        (predictions_howmany_50, predictions_howmany_85, predictions_howmany_95) = monte_carlo_service.how_many(target_date, closed_items_history)       
    
    
    ## Run When Predictions via Monte Carlo Simulation - only possible if we have an item tag set to fetch how many items are remaining
    predictions_when_50 = predictions_when_85 = predictions_when_95 = datetime.date.today()
    predictions_targetdate_likelyhood = None
    
    if release_tag:
        remaining_items = get_remaining_items_by_tag_and_type(prediction.work_item_types, release_tag)            
        prediction.remaining_items = remaining_items            
        if remaining_items > 0:              
            (predictions_when_50, predictions_when_85, predictions_when_95, predictions_targetdate_likelyhood) = monte_carlo_service.when(remaining_items, closed_items_history, target_date)
    
    add_forecast_to_prediction(prediction, predictions_howmany_50, predictions_howmany_85, predictions_howmany_95, predictions_when_50, predictions_when_85, predictions_when_95, target_date, predictions_targetdate_likelyhood)
    
    ## Run Sprint Predictions
    if "User Story" in prediction.work_item_types and (iteration_length or goal_tag):       
        iteration_prediction = Prediction(["Iteration"], True, 90, "Closed", [])
        
        print("Read Sprint Prediction settings: Iteration Length is {0} and Tag is {1}".format(iteration_length, goal_tag))
        
        predictions_when_50 = predictions_when_85 = predictions_when_95 = datetime.date.today()
        predictions_targetdate_likelyhood = None
        
        if goal_tag:
            print("Checking how many items with tag '{0}' are pending".format(goal_tag))
            remaining_items_for_sprint = get_remaining_items_by_tag_and_type(prediction.work_item_types, goal_tag)      
            iteration_prediction.remaining_items = remaining_items_for_sprint
            
            if remaining_items_for_sprint >= 1:
                print("{0} '{1}' Items are pending...".format(remaining_items_for_sprint, goal_tag))
                (predictions_when_50, predictions_when_85, predictions_when_95, predictions_targetdate_likelyhood) = monte_carlo_service.when(remaining_items_for_sprint, closed_items_history, datetime.date.today())
            else:
                print("No remaining items left - skipping prediction")
        
        predictions_howmany_50 = predictions_howmany_85 = predictions_howmany_95 = 0
        iteration_target_date = datetime.date.today()
        if iteration_length:
            print("Checking how many items can be done in the next {0} days".format(iteration_length))
            iteration_target_date = (datetime.datetime.now() + datetime.timedelta(days = iteration_length)).date()
            
            (predictions_howmany_50, predictions_howmany_85, predictions_howmany_95) = monte_carlo_service.how_many(iteration_target_date, closed_items_history)
        
        add_forecast_to_prediction(iteration_prediction, predictions_howmany_50, predictions_howmany_85, predictions_howmany_95, predictions_when_50, predictions_when_85, predictions_when_95, iteration_target_date, predictions_targetdate_likelyhood)
        
        predictions.append(iteration_prediction)
        
print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
print("Summary")
print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

for prediction in predictions:            
    print("================================================================")
    if prediction.run_prediction == False:            
        print("Predictions for {0} disabled - skipping".format(prediction.work_item_types))
        print("================================================================")
        continue
    
    print("Predictions for {0}:".format(prediction.work_item_types))
    print("================================================================")
    
    print("How many items will be done by {0}:".format(prediction.target_date))
    print("50%: {0}".format(prediction.how_many_50))
    print("85%: {0}".format(prediction.how_many_85))
    print("95%: {0}".format(prediction.how_many_95))
    print("----------------------------------------")
    
    if prediction.remaining_items != 0:
        print("When will {0} items be done:".format(prediction.remaining_items))
        print("50%: {0}".format(prediction.when_50))
        print("85%: {0}".format(prediction.when_85))
        print("95%: {0}".format(prediction.when_95))
        print("----------------------------------------")
        print("Chance of Target Date: {0} - {1}".format(target_date, prediction.target_date_likelyhood))