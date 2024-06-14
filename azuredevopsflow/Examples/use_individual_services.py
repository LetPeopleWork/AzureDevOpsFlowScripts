from FlowMetricsCSV.FlowMetricsService import FlowMetricsService
from MonteCarloCSV.MonteCarloService import MonteCarloService
from AzureDevOpsFlow.WorkItemService import WorkItemService

from datetime import datetime, timedelta

# Azure DevOps Settings
org_url = "https://dev.azure.com/YourOrg"
api_token = "YOUR API TOKEN"
estimation_field = "Microsoft.VSTS.Scheduling.StoryPoints"
history_in_days = 90

# Create Work Item Service
work_item_service = WorkItemService(org_url, api_token, estimation_field, history_in_days)

# Item Query to get all items in a teams backlog
item_query = '([System.WorkItemType] = "User Story" or [System.WorkItemType] = "Bug") AND [System.TeamProject] == "Your Project" AND [System.AreaPath] UNDER "Team Project\\Team Name"'

# Get Work Items and filter out not started ones
work_items = work_item_service.get_items_via_wiql(item_query)
work_items = [item for item in work_items if item.started_date is not None]

# Create Flow Metrics Service to draw charts
flow_metrics_service = FlowMetricsService(False, "Charts")

# Draw Cycle Time Scatterplot with Work Items from item Query and chart settings
percentiles = [65, 74, 90]
percentile_colors = ["red", "orange", "green"]
flow_metrics_service.plot_cycle_time_scatterplot(work_items, 14, percentiles, percentile_colors, "Cycle Time Scatterplot")

# Create Monte Carlo Service to run MCS
monte_carlo_service = MonteCarloService(history_in_days, False)

# Filter for closed items and create throughput history
closed_items = [item for item in work_items if item.closed_date is not None]
throughput_history = monte_carlo_service.create_closed_items_history(closed_items)

# Forecast how many items we can do in the next x days (alterantively use a fixed date)
days_in_future = 14
target_date = (datetime.now() + timedelta(days_in_future)).date()

(percentile_50, percentile_70, percentile_85, percentile_95) = monte_carlo_service.how_many(target_date, throughput_history)

print("How Many Forecasts: 50% Chance: {0} - 70% Chance: {1} - 85% Chance: {2} - 95% Chance: {3}".format(percentile_50, percentile_70, percentile_85, percentile_95))

# Get "remaining items" based on query
remaining_items_query = '([System.WorkItemType] = "User Story" or [System.WorkItemType] = "Bug") AND [System.TeamProject] == "Team Project" AND ([System.State] <> "Done" AND [System.State] <> "Removed") AND [System.AreaPath] UNDER "Team Project\\Team Name" AND [System.Tags] CONTAINS "Sprint Goal"'
remaining_items = len(work_item_service.get_items_via_wiql(remaining_items_query))

# Forecast When Items will be done (if you specify a target date, you'll get a likelihood)
target_date = datetime.strptime("2024-08-31", "%Y-%m-%d").date()
# target_date can also be skipped --> target_date = None

(predicted_date_50, predicted_date_70, predicted_date_85, predicted_date_95, target_date_likelyhood) = monte_carlo_service.when(remaining_items, throughput_history, target_date)

print("When Forecast: 50% Chance: {0} - 70% Chance: {1} - 85% Chance: {2} - 95% Chance: {3} - Likelihood: {4}".format(predicted_date_50, predicted_date_70, predicted_date_85, predicted_date_95, target_date_likelyhood))