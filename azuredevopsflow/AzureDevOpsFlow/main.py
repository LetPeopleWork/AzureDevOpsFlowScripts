import argparse
import os
import shutil
import json

from datetime import datetime, timedelta

from FlowMetricsCSV.FlowMetricsService import FlowMetricsService
from MonteCarloCSV.MonteCarloService import MonteCarloService

from .WorkItemService import WorkItemService

def print_logo():
    logo = r"""
    /$$                 /$$           /$$$$$$$                           /$$                /$$      /$$                  /$$      
    | $$                | $$          | $$__  $$                         | $$               | $$  /$ | $$                 | $$      
    | $$       /$$$$$$ /$$$$$$        | $$  \ $$/$$$$$$  /$$$$$$  /$$$$$$| $$ /$$$$$$       | $$ /$$$| $$ /$$$$$$  /$$$$$$| $$   /$$
    | $$      /$$__  $|_  $$_/        | $$$$$$$/$$__  $$/$$__  $$/$$__  $| $$/$$__  $$      | $$/$$ $$ $$/$$__  $$/$$__  $| $$  /$$/
    | $$     | $$$$$$$$ | $$          | $$____| $$$$$$$| $$  \ $| $$  \ $| $| $$$$$$$$      | $$$$_  $$$| $$  \ $| $$  \__| $$$$$$/ 
    | $$     | $$_____/ | $$ /$$      | $$    | $$_____| $$  | $| $$  | $| $| $$_____/      | $$$/ \  $$| $$  | $| $$     | $$_  $$ 
    | $$$$$$$|  $$$$$$$ |  $$$$/      | $$    |  $$$$$$|  $$$$$$| $$$$$$$| $|  $$$$$$$      | $$/   \  $|  $$$$$$| $$     | $$ \  $$
    |________/\_______/  \___/        |__/     \_______/\______/| $$____/|__/\_______/      |__/     \__/\______/|__/     |__/  \__/
                                                        | $$                                                                
                                                        | $$                                                                
                                                        |__/                                                                
    """
    print(logo)
    
def copy_default_config(script_dir):        
    default_config_file = os.path.join(script_dir, "ExampleConfig.json")
    
    config_file_destination = os.path.join(os.getcwd(), os.path.basename(default_config_file))        
    if not check_if_file_exists(config_file_destination):
        shutil.copy(default_config_file, config_file_destination)

def check_if_file_exists(file_path, raise_if_not_found = False):
    if not os.path.isfile(file_path):
        if raise_if_not_found:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        return False
    
    return True

def read_config(file_path):
    print("Reading Config File from {0}".format(file_path))
    
    check_if_file_exists(file_path, True)
    
    with open(file_path, 'r') as file:
        config_data = json.load(file)
    return config_data

def main():
    try:
        print_logo()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--ConfigFileNames", type=str, nargs='+', default=[])

        args = parser.parse_args()
        
        config_paths = args.ConfigFileNames
        
        if len(config_paths) < 1:
            print("No config file specified, copying defaults and using them")
            copy_default_config(script_dir)
            config_paths.append("ExampleConfig.json")
        
        print("Using following configuration files: {0}".format(config_paths))

        for config_path in config_paths:
            print("================================================================")
            config = read_config(config_path)
            
            # Azure DevOps COnfig
            org_url = config["azureDevOps"]["organizationUrl"]
            api_token = config["azureDevOps"]["apiToken"]
            item_query = config["azureDevOps"]["itemQuery"]
            history_in_days = int(config["azureDevOps"]["historyInDays"])
            estimation_field = config["azureDevOps"]["estimationField"]
            
            work_item_service = WorkItemService(org_url, api_token, estimation_field, history_in_days)
            
            work_items = work_item_service.get_items_via_wiql(item_query)
            work_items = [item for item in work_items if item.started_date is not None]
            
            # General Config
            show_plots = config["general"]["showPlots"]
            charts_folder = config["general"]["chartsFolder"]
            
            flow_metrics_service = FlowMetricsService(show_plots, charts_folder)
            
            print("Creating Charts as per the configuration...")
            print("----------------------------------------------------------------")   
            
            if len(work_items) < 1:
                print("No items - skipping")
                exit()
                
            def run_forecasts():
                forecasts = config["forecasts"]
                
                monte_carlo_service = MonteCarloService(history_in_days, True)
                
                closed_items = [item for item in work_items if item.closed_date is not None]
                throughput_history = monte_carlo_service.create_closed_items_history(closed_items)
                
                for forecast in forecasts:                    
                    print("Running Forecast for {0}".format(forecast["name"]))
                    remaining_items_query = forecast["remainingBacklogQuery"]
                    target_date = forecast["targetDate"]
                    
                    if isinstance(target_date, int):
                        target_date = (datetime.now() + timedelta(target_date)).date()
                    else:
                        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                    
                    remaining_items = work_item_service.get_items_via_wiql(remaining_items_query)
                    
                    monte_carlo_service.how_many(target_date, throughput_history)
                    monte_carlo_service.when(len(remaining_items), throughput_history, target_date)

            def create_cycle_time_scatterplot():
                chart_config = config["cycleTimeScatterPlot"]

                if chart_config["generate"]:
                    flow_metrics_service.plot_cycle_time_scatterplot(work_items, chart_config["history"], chart_config["percentiles"], chart_config["percentileColors"], chart_config["chartName"])

            def create_work_item_age_scatterplot():
                chart_config = config["workItemAgeScatterPlot"]

                if chart_config["generate"]:
                    flow_metrics_service.plot_work_item_age_scatterplot(work_items, chart_config["history"], chart_config["xAxisLines"], chart_config["xAxisLineColors"], chart_config["chartName"])

            def create_throughput_run_chart():
                chart_config = config["throughputRunChart"]

                if chart_config["generate"]:
                    flow_metrics_service.plot_throughput_run_chart(work_items, chart_config["history"], chart_config["chartName"], chart_config["unit"])            

            def create_work_in_process_run_chart():
                chart_config = config["workInProcessRunChart"]

                if chart_config["generate"]:
                    flow_metrics_service.plot_work_in_process_run_chart(work_items, chart_config["history"], chart_config["chartName"])

            def create_work_started_vs_finished_chart():
                chart_config = config["startedVsFinishedChart"]

                if chart_config["generate"]:
                    flow_metrics_service.plot_work_started_vs_finished_chart(work_items, chart_config["history"], chart_config["startedColor"], chart_config["closedColor"], chart_config["chartName"])

            def create_estimation_vs_cycle_time_chart():
                chart_config = config["estimationVsCycleTime"]

                if chart_config["generate"]:
                    flow_metrics_service.plot_estimation_vs_cycle_time_scatterplot(work_items, chart_config["history"], chart_config["chartName"], chart_config["estimationUnit"])

            def create_process_behaviour_charts():
                chart_config = config["processBehaviourCharts"]

                if chart_config["generate"]:
                    history = chart_config["history"]
                    baseline_start = datetime.strptime(chart_config["baselineStart"], "%Y-%m-%d")
                    baseline_end = datetime.strptime(chart_config["baselineEnd"], "%Y-%m-%d")

                    flow_metrics_service.plot_throughput_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["throughputChartName"])            
                    flow_metrics_service.plot_wip_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["wipChartName"])
                    flow_metrics_service.plot_cycle_time_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["cycleTimeChartName"])       
                    flow_metrics_service.plot_total_age_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["itemAgeChartName"])                        

            print("---------------------------")
            print("Creating Charts...")
            create_cycle_time_scatterplot()
            create_work_item_age_scatterplot()
            create_throughput_run_chart()
            create_work_in_process_run_chart()
            create_work_started_vs_finished_chart()
            create_estimation_vs_cycle_time_chart()    
            create_process_behaviour_charts()       
            
            print("---------------------------")
            print("Running Forecasts")
            run_forecasts()

            print()
            print()
            print()
            print("🛈 Want to learn more about how all of this works? Check out out website! 🛈")
            print("🔗 https://letpeople.work 🔗")
    except Exception as exception:
        print("Error while executing azuredevopsflow:")
        print(exception)
        
        print("🪲 If the problem cannot be solved, consider opening an issue on GitHub: https://github.com/LetPeopleWork/AzureDevOpsFlowScripts/issues 🪲")

if __name__ == "__main__":    
    main()