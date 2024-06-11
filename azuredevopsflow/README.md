# Flow Metrics CSV
This python package allows you to visualize the four measures of flow based on any csv file. It can be run offline, and all it needs is a csv file with the start and closing dates of the items. Items that are still in progress, have no value for the closed date. Feel free to check out the code, propose improvements and also make it your own by adjusting it to your context and potentially integrating it into some kind of pipeline of yours. The true power of Flow Metrics comes when inspected on a regular base. The point of collecting data is to take action, so use this to make informed decisions about what you want to adjust! You can use this for free, hope it helps.

This tool is provided for free by [LetPeopleWork](https://letpeople.work). If you are curious about Flow Metrics, Kanban, #NoEstimates etc., feel free to reach out to us and book a call!

## Installation
Make sure you have python 3.x installed on your system and it's available via your PATH variable. You can check this by running `python --version` on your terminal. If it works without error, you have python installed and ready. If not, you can download it from the [official Python Website](https://www.python.org/downloads/).

**Important:** It can be that you have to use `python3 --version`. If this is the case, please use always `python3` instead of `python` in the following commands.

Once you have made sure python is installed, you can download `flowmetricscsv` via pip:
`python -m pip install --upgrade flowmetricscsv`

## Run flowmetricscsv
If your installation was successfull, you can now run `flowmetricscsv` via the commandline. When not supplied with any parameter for a configuration file, it will automatically copy the `ExampleConfig.json` and will auto-generate an `ExampleFile.csv` to your current directory and use those to generate the charts. After you've run `flowmetricscsv` you should have the 2 files in your current directory as well as a folder called `Charts` that includes the generated from the example data.

You can now start to tweak the configuration and replace the csv file according to your needs.
**Note**: It's recommended to rename your config file from *ExampleConfig.json* to something more meaningful (like *TeamNameConfig.json*) and to specify this configuration file when running it again: `flowmetricscsv --ConfigFileNames "TeamNameConfig.json"`.

Read on to see details about how to configure `flowmetricscsv`.

## Create Flow Metrics Visulization
To create the visulizations with `flowmetricscsv`, you need various inputs. First and foremost, you need to provide a csv file that includes the date when an item was started and closed (unless it's still in progress). The csv can contain other information, but it's not needed nor relevant for any of the visulizations. Using the "history" parameter, you can define which perioud you want to visualize. Do you want to see the last 30 days or rather the last 90 days?

## Configuration
In the [ExampleConfig.json](https://github.com/LetPeopleWork/FlowMetricsCSV/blob/main/ExampleConfig.json) file you can see the default configuration. There are general settings and configurations per chart. Below you can find a summary of the various options.

<details>
  <summary>Sample Configuration</summary>
  ```json
{
    "general": {
        "fileName": "ExampleFile.csv",
        "delimeter": ";",
        "startedDateColumn": "Activated Date",
        "closedDateColumn": "Closed Date",
        "startDateFormat": "%m/%d/%Y %I:%M:%S %p",
        "closedDateFormat": "",
        "estimationColumn": "Story Points",
        "itemTitleColumn": "ID",
        "chartsFolder": "Charts",
        "showPlots": false
    },
    "cycleTimeScatterPlot": {
        "generate": true,
        "history": 180,
        "chartName": "CycleTime.png",
        "percentiles": [50, 70, 85, 95],
        "percentileColors": ["red", "orange", "lightgreen", "darkgreen"]
    },
    "workItemAgeScatterPlot": {
        "generate": true,
        "history": 180,
        "chartName": "WorkItemAge.png",
        "xAxisLines": [5, 10],
        "xAxisLineColors": ["orange", "red"]
    },
    "throughputRunChart": {
        "generate": true,
        "history": 180,
        "unit": "days",
        "chartName": "Throughput.png"
    },
    "workInProcessRunChart": {
        "generate": true,
        "history": 180,
        "chartName": "WorkInProcess.png"
    },
    "startedVsFinishedChart": {
        "generate": true,
        "history": 180,
        "chartName": "StartedVsFinished.png",
        "startedColor": "orange",
        "closedColor": "green"
    },
    "estimationVsCycleTime": {
        "generate": true,
        "history": 180,
        "chartName": "EstimationVsCycleTime.png",
        "estimationUnit": "Story Points"
    },
    "processBehaviourCharts": {
        "generate": true,
        "baselineStart": "2024-01-01",
        "baselineEnd": "2024-01-31",
        "history": 60,
        "throughputChartName": "Throughput_PBC.png",
        "cycleTimeChartName": "CycleTime_PBC.png",
        "wipChartName": "WorkInProgress_PBC.png",
        "itemAgeChartName": "WorkItemAge_PBC.png"
    }
}
  ```
</details>

### General

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| FileName               | The name of the CSV file you want to use as input. Can be a relative path from the script location (like in the example) or a full path if the files are somewhere else.             | ExampleFile.csv   |
| Delimeter              | The delimiter used in the CSV file   | ;                  |
| StartedDateColumn      | The name of the column in the csv file that contains the started date       | Activated Date     |
| ClosedDateColumn       | The name of the column in the csv file that contains the closed date          | Closed Date        |
| StartDateFormat        | The format of the start dates in the csv file. Default is "%m/%d/%Y %I:%M:%S %p". Check [Python Dates](https://www.w3schools.com/python/python_datetime.asp) for the options you have (or ask ChatGPT)       | %m/%d/%Y %I:%M:%S %p|
| ClosedDateFormat       | The format of the closed dates in the csv file. If not set (default), the same format as specified for the start date is used. Check [Python Dates](https://www.w3schools.com/python/python_datetime.asp) for the options you have (or ask ChatGPT)          | None |
| estimationColumn       | The name of the column in the csv file that contains the estimations (optional). This is needed if you want to plot a chart where you compare estimates vs. cycle-time.          | Story Points        |
| itemTitleColumn       | The name of the column in the csv file that contains the title of the items (optional). This can be anything to identify the item, like an ID or some other text. If set, it will display the text next to the bubbles in the charts. Note that the shorter the text, the easier it is to read. Long texts will overlap.          | ID        |
| ChartsFolder           | Folder path for the folder where the charts should be saved. Can be relative to the script location (like the default) or a full path to a folder. Folder does not need to exist, it will be created as part of the script.               | Charts             |
| ShowPlots              | If set to true, the script will stop and show you an interactive version of the chart before continuing.                | false              |

### Cycle Time Scatter Plot

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| Generate               | Whether to generate the chart at all. If set to false, no further settings need to be specified.        | true               |
| History                | Defines how much data should be used. It's always calculated from today backwards. The value is in days.      | 30                 |
| ChartName              | File name of the chart.     | CycleTime.png      |
| Percentiles            | List of which percentiles should be shown in the chart. Can be any value from 1 to 100.     | [50, 70, 85, 95]    |
| PercentileColors       | Colors for the percentiles defined. The amount has to match with what you specified above. Colors are associated by sequence. | [red, orange, lightgreen, darkgreen]|

### Work Item Age Scatter Plot

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| Generate               | Whether to generate the chart at all. If set to false, no further settings need to be specified.         | true               |
| History                | Defines how much data should be used. It's always calculated from today backwards. The value is in days.      | 30                 |
| ChartName              | File name of the chart.       | WorkItemAge.png    |
| XAxisLines             | List of which lines should be shown on the x-axis (in days). This can be useful to track if your items approach their [Service Level Expectation](https://kanbanguides.org/english/).      | [5, 10]            |
| XAxisLineColors        | Colors for corresponding X-axis lines. The amount has to match with what you specified above. Colors are associated by sequence. | [orange, red]      |

### Throughput Run Chart

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| Generate               | Whether to generate the chart at all. If set to false, no further settings need to be specified.         | true               |
| History                | Defines how much data should be used. It's always calculated from today backwards. The value is in days.      | 90                 |
| Unit                   | Which grouping is applied. Possible options are 'days', 'weeks', and 'months'    | days               |
| ChartName              | File name of the chart.               | Throughput.png     |

### Work In Process Run Chart

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| Generate               | Whether to generate the chart at all. If set to false, no further settings need to be specified.         | true               |
| History                | Defines how much data should be used. It's always calculated from today backwards. The value is in days.      | 30                 |
| ChartName              | File name of the chart.                 | WorkInProcess.png  |

### Started Vs FinishedChart

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| Generate               | Whether to generate the chart at all. If set to false, no further settings need to be specified.         | true               |
| History                | Defines how much data should be used. It's always calculated from today backwards. The value is in days.      | 90                 |
| ChartName              | File name of the chart.          | StartedVsFinished.png|
| StartedColor           | Color for started items on the chart  | orange             |
| ClosedColor            | Color for closed items on the chart   | green              |


### Estimation Vs CycleTime

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| Generate               | Whether to generate the chart at all. If set to false, no further settings need to be specified. If enabled, `estimationColumn` must be set and available in the CSV.         | false               |
| History                | Defines how much data should be used. It's always calculated from today backwards. The value is in days.      | 90                 |
| ChartName              | File name of the chart.          | EstimationVsCycleTime.png|
| estimationUnit         | Unit of estimation that will be visible on the chart. Examples: Story Points, Hours, Ideal Days etc.          | Story Points |

### Process Behaviour Chars

| Name                   | Description                          | Default Value      |
|------------------------|--------------------------------------|--------------------|
| Generate               | Whether to generate the chart at all. If set to false, no further settings need to be specified. If enabled, process behaviour charts for all 4 measures of flow will be generated.         | true               |
| BaselineStart          | The start date for your baseline for the PBCs. Follows the format "yyyy-MM-dd". The baseline is what defines the visualized average, as well as the upper and lower natural process limit.        | 2024-01-01               |
| BaselineEnd            | The end date for your baseline for the PBCs. Follows the format "yyyy-MM-dd". The baseline is what defines the visualized average, as well as the upper and lower natural process limit.      | 2024-01-31               |
| History                | Defines how much data should be used. It's always calculated from today backwards. The value is in days.      | 60                 |
| ThroughputChartName    | File name of the Throughput PBC chart.          | Throughput_PBC.png|
| CycleTimeChartName     | File name of the Cycle Time PBC chart.          | CycleTime_PBC.png|
| WipChartName           | File name of the WIP PBC chart.          | WorkInProgress_PBC.png|
| ItemAgeChartName       | File name of the Total Work Item Age PBC chart.          | WorkItemAge_PBC.png|

## Running flowmetricscsv with multiple Configurations
You can have multiple configurations that you can use to create different charts. For example for different teams or different item types (for example if you want to visualize Epics differently than other work items).
Each configuration is independent and can work against different input files. If you want to generate many charts at once with different configurations, you can also specify multiple configuration files:
`flowmetricscsv --ConfigFileNames "TeamA_Config.json" "TeamB_Config.json" "TeamC_Config.json"`

This will generate you three sets of charts as per the individual configurations specified.
**Note:** Make sure to specify different folders or chart names in the respective configs, as otherwise they will be overwritten.

# How to use the created charts?
You find more information on this in the [wiki](https://github.com/LetPeopleWork/FlowMetricsCSV/wiki)

# Usage of flowmetricscsv in other python scripts
If you want to reuse `flowmetricscsv` in your own python scripts, you can do so in two ways described below.
This might be useful if you generate a csv in python and want to directly pass it to `flowmetricscsv` to generate charts, or you simply want to reuse dedicated functions to generate specific charts.

## Call with sys args
You can simply invoke the whole program and specify which configuration file to use, by using `sys.argv`. You can find an example in the following file in the *Examples* folder: [call_via_sys.py](https://github.com/LetPeopleWork/FlowMetricsCSV/blob/main/Examples/call_via_sys.py)

## Generate Specific Charts
If you don't want to call the full application, but you either want to create only specific charts or not bother creating the config file, you can also call dedicated functions from the `FlowMetricsService`.
You don't need the config file for this, but you have to supply different parameters to the functions yourself that otherwise are read from the config file. You also must specify all the work items that are of type [WorkItem](https://github.com/LetPeopleWork/FlowMetricsCSV/blob/main/FlowMetricsCSV/WorkItem.py) as input to the functions. The easiest way is to use the provided [CsvService](https://github.com/LetPeopleWork/FlowMetricsCSV/blob/main/FlowMetricsCSV/CsvService.py) to parse an existing csv file. But you can also use other ways to generate the `WorkItem` objects.

In the Example folder, you find one example on how you can use this in the file [use_individual_services.py](https://github.com/LetPeopleWork/FlowMetricsCSV/blob/main/Examples/use_individual_services.py).

### FlowMetricService Functions
Following is an overview over the functions the [FlowMetricsService](https://github.com/LetPeopleWork/FlowMetricsCSV/blob/main/FlowMetricsCSV/FlowMetricsService.py) is providing.

#### Initialization
To initialize the service, provide parameters `show_plots` (boolean) and `charts_folder` (string) which represents whether to show plots immediately and the folder to store generated charts respectively.

#### Plot Functions
| Function | Description |
|----------|-------------|
| `plot_cycle_time_scatterplot` | Creates a scatterplot of Cycle Time against Work Item Closed Date with percentiles. |
| `plot_work_item_age_scatterplot` | Generates a scatterplot of Work Item Age against Work Item Started Date with optional x-axis lines. |
| `plot_throughput_run_chart` | Plots Throughput Run Chart displaying items completed over time. |
| `plot_work_in_process_run_chart` | Creates a Work In Process (WIP) Run Chart showing the number of items in process over time. |
| `plot_work_started_vs_finished_chart` | Generates a chart comparing Work Items started vs. finished over time. |
| `plot_estimation_vs_cycle_time_scatterplot` | Plots Estimation vs. Cycle Time scatterplot. |
| `plot_total_age_process_behaviour_chart` | Generates Total Work Item Age Process Behavior Chart. |
| `plot_cycle_time_process_behaviour_chart` | Creates Cycle Time Process Behavior Chart. |
| `plot_wip_process_behaviour_chart` | Generates Work In Process (WIP) Process Behavior Chart. |
| `plot_throughput_process_behaviour_chart` | Plots Throughput Process Behavior Chart. |