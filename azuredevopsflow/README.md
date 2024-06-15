# Azure DevOps Flow
This python package allows you to visualize your measures of flow as well as to run Monte Carlo Simulations based on the data in your Azure DevOps Backlog. All it needs is a connection to your Azure DevOps via [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows) and the queries to your backlog. Feel free to check out the code, propose improvements and also make it your own by adjusting it to your context and potentially integrating it into some kind of pipeline of yours. The true power of Flow Metrics comes when inspected on a regular base. The point of collecting data is to take action, so use this to make informed decisions about what you want to adjust! You can use this for free, hope it helps.

This tool is provided for free by [LetPeopleWork](https://letpeople.work). If you are curious about Flow Metrics, Kanban, #NoEstimates etc., feel free to reach out to us and book a call!

## Installation
Make sure you have python 3.x installed on your system and it's available via your PATH variable. You can check this by running `python --version` on your terminal. If it works without error, you have python installed and ready. If not, you can download it from the [official Python Website](https://www.python.org/downloads/).

**Important:** It can be that you have to use `python3 --version`. If this is the case, please use always `python3` instead of `python` in the following commands.

Once you have made sure python is installed, you can download `azuredevopsflow` via pip:
`python -m pip install --upgrade azuredevopsflow`

## Run azuredevopsflow
If your installation was successfull, you can now run `azuredevopsflow` via the commandline. When not supplied with any parameter for a configuration file, it will automatically copy the `ExampleConfig.json` to your current directory and run using. This will fail with the following error `TF400813: The user 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa' is not authorized to access this resource.` as you must configure your connection to Azure DevOps first.
**Note**: It's recommended to rename your config file from *ExampleConfig.json* to something more meaningful (like *TeamNameConfig.json*) and to specify this configuration file when running it again: `azuredevopsflow --ConfigFileNames "TeamNameConfig.json"`.

### Running azuredevopsflow with multiple Configurations
You can have multiple configurations that you can use to create different charts and/or run different forecasts. For example for different teams or different item types (for example if you want to visualize Epics differently than other work items).
Each configuration is independent and can work against different input files. If you want to generate many charts/forecasts at once with different configurations, you can also specify multiple configuration files:
`azuredevopsflow --ConfigFileNames "TeamA_Config.json" "TeamB_Config.json" "TeamC_Config.json"`

This will generate you three sets of charts as per the individual configurations specified.
**Note:** Make sure to specify different folders or chart names in the respective configs, as otherwise they will be overwritten.

Read on to see details about how to configure `azuredevopsflow`.

## Configuration
In the [ExampleConfig.json](https://github.com/LetPeopleWork/AzureDevOpsFlowScripts/tree/main/azuredevopsflow/AzureDevOpsFlow/ExampleConfig.json) file you can see the default configuration.
There are general settings, Azure DevOps specific settings, configurations per chart you want to create and specific forecast settings. Below you can find a summary of the various options.

### General

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| ChartsFolder           | Folder path for the folder where the charts should be saved. Can be relative to the script location (like the default) or a full path to a folder. Folder does not need to exist, it will be created as part of the script.               | Charts             |
| ShowPlots              | If set to true, the script will stop and show you an interactive version of the chart before continuing.                | false              |

### Azure DevOps Settings
In order to make any use of `azuredevopsflow`, you must specify against which Azure DevOps organization you are working. For this you need a url, as well as a [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows). Furthermore you have to specify a query that gets the items of the team(s) you are interested in as well as how many days into the past you are interested in. Last but not least, you can specify which field you are using for estimates. The queries are written in [WIQL](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops).

**Important**: Double Quotes (") as well as backslashes (\\) cannot be written in json like this. You have to "escape" it by prepending a \\. Thus if you want to write a ", you have to type \\". If you want to use a backslash, you must write \\\\. Please reference the example configurations default values.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| organizationUrl           | The url to your Azure DevOps Organization. Replace _YourOrg_ with your actual organization name.               | https://dev.azure.com/YourOrg             |
| apiToken              | [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows) to access the data in your organization             | ""              |
| itemQuery           | The query to get your teams items. Note that this should contain all items that are relevant for your team, closed, in progress, and not started. Check out the [WIQL reference](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) if you need support.             | ([System.WorkItemType] = \"User Story\" or [System.WorkItemType] = \"Bug\") AND [System.TeamProject] == \"Your Project\" AND [System.AreaPath] UNDER \"Team Project\\\\Team Name\"             |
| historyInDays           | How many days in the past you look for items               | 90             |
| estimationField           | Which field is holding the estimates. You can see the "reference Name" for the fields if you browse to *https://dev.azure.com/%7Borganization%7D/%7Bproject%7D/_apis/wit/fields?api-version=7.1-preview.3* - and insert your organization and project            | Microsoft.VSTS.Scheduling.StoryPoints             |

### Forecast Settings
You can add one or more forecasts. Forecasts need two inputs: The remaining items you want to forecast (when will they be done?) and a target date (how much can we get done till then). The target date is specified either as a date in the format *YYYY-mm-dd* or as number. If you specify a number, it will use the date that is this amount of days in the future. To get the remaining items, you specify a query that returns all items that are not yet done and you want to forecast. You can use all filters WIQL has to offer, for example filtering by area path, tag, iteration path, or anything else.

If you don't provide a *target date*, no "How Many" simulation will be run. If you don't provide a *remaining Backlog Query*, no "When" simulation will be run. If you provide both, you'll get a on top a likelihood of reaching the target date with the remaining backlog.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| name           | The name of your Forecast.               | "Release 23.44" or "Sprint Goal"             |
| remainingBacklogQuery           | The query to get the remaining items for your forecast. Note that this should contain all items that are relevant for your forecast, so most likely you want to filter out closed and removed items. Check out the [WIQL reference](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) if you need support.             | ([System.WorkItemType] = \"User Story\" or [System.WorkItemType] = \"Bug\") AND [System.TeamProject] == \"Your Project\" AND ([System.State] <> \"Closed\" AND [System.State] <> \"Removed\") AND [System.AreaPath] UNDER \"Team Project\\Team Name\" AND [System.Tags] CONTAINS \"Release 24.10\"|
| targetDate           | Either the date in *YYYY-mm-dd* format or the number of days in future               | "2024-10-31" / 14             |

#### Skip Forecasts
If you don't want to run any forecasts, just remove all forecasts, so that your config looks like this:
```
"forecasts":[
    ],
```

### Chart Settings
Every chart can be configured with different settings. You can also switch off the generation of a sepcific chart by setting `generate: false`.
You can find detailed information to the possible chart configurations in [FlowMetricsCSV](https://github.com/LetPeopleWork/FlowMetricsCSV?tab=readme-ov-file#cycle-time-scatter-plot).


After you configured `azuredevopsflow` with your queries and with your token, you are ready to go. simply run `azuredevopsflow --ConfigFileNames "YourConfig.json"`. It will generate all the charts according to your configurations and will show you your forecasts in the commandline.

## How to use the created charts?
You find more information on this in the [wiki](https://github.com/LetPeopleWork/FlowMetricsCSV/wiki)

## How to build your own Applications on Top of this Package?
If you have additional demands, like running the forecasts on a regular base and pushing the results somewhere (like in a database) instead of just displaying it in the commandline, you can build your own python application on top.

After you installed the package, you can include the following services and then run your own applications on top:
```
from FlowMetricsCSV.FlowMetricsService import FlowMetricsService
from MonteCarloCSV.MonteCarloService import MonteCarloService
from AzureDevOpsFlow.WorkItemService import WorkItemService
```

You can create the various services and provide the necessary configuration as it best fits you:
```
work_item_service = WorkItemService(org_url, api_token, estimation_field, history_in_days)
flow_metrics_service = FlowMetricsService(False, "Charts")
monte_carlo_service = MonteCarloService(history_in_days, False)
```

Using those services, you can get the data from Azure DevOps via WIQL, transform it to create your charts, and run forecasts:
```
work_items = work_item_service.get_items_via_wiql(item_query)
work_items = [item for item in work_items if item.started_date is not None]

flow_metrics_service.plot_cycle_time_scatterplot(work_items, 14, percentiles, percentile_colors, "Cycle Time Scatterplot")

closed_items = [item for item in work_items if item.closed_date is not None]
throughput_history = monte_carlo_service.create_closed_items_history(closed_items)

(percentile_50, percentile_70, percentile_85, percentile_95) = monte_carlo_service.how_many(target_date, throughput_history)

(predicted_date_50, predicted_date_70, predicted_date_85, predicted_date_95, target_date_likelyhood) = monte_carlo_service.when(remaining_items, throughput_history, target_date)
```

See [Github](https://github.com/LetPeopleWork/AzureDevOpsFlowScripts/blob/main/azuredevopsflow/Examples/use_individual_services.py) for a full example of how you can use this.