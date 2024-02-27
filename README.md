# AzureDevOpsPythonScripts

## Download Files
In order to run the scripts, you need to download all the files in this repository. There are dependencies between the files so you cannot just download a single file. Please always use the full folder structure.

## Install Prerequisites
Make sure you have python 3.x installed on your system and it's available via your PATH variable.

Then run `python -m pip install -r .\requirements.txt` from this directory to install the packages.

## Run Monte Carlo (MC) Simulations
Let's you run MC Simulations based on your items in Azure DevOps.
The script supports "How Many" and "When" simulations, forecasting how many items till a specific date might be done as well as when 'x' amount of items will be done (based on tags).

The script will only read data from your Azure DevOps Organization, so you won't need any special permissions.
You can run it as follows from your local machine:
`python .\MonteCarlo.py --OrganizationUrl "https://dev.azure.com/huserben/" --PersonalAccessToken "***********" --ReleaseTag "MyProduct v1.33.7" --TargetDate "08.04.2024" --GoalTag "SprintGoal" --IterationLength "7"`

- This will run the MC Simulations against items in the Azure DevOps org *huserben*.
- It will forecast how long it will take to close the items that contain a tag called *MyProduct v1.33.7*.
- It will forecast how many items you'll be able to close till *08.04.2024*
- Furthermore it will calculate how long it will take to close items tagged with *SprintGoal* and how many items you'll be able to close within the next *7* days

The results will be presented in the output. At the end of the script there will be a summary with the forecasts.

Feel free to adjust the script based on your need, for example by adding a way to export the data.

**Note:** While it's ok to run it manually, I highly advise to run the script continuously. See *Pipeline Integration* at the bottom.

### Prediction Configuration
You can configure predictions as part of the script (see line 30 in *MonteCarlo.py* that starts with `predictions = [...`).

You can run predictions per "Work Item Type". For example you can run the predictions for your Epics and another forecast for your User Stories & Bugs.

Adjust the following lines as you wish in the script:

```
predictions = [ Prediction(["Epic"], False, 180, ["Closed", "Resolved"], ["MyProduct\MyAreaPath"]),
                Prediction(["User Story", "Bug"], True, 90, ["Closed"], ["MyProduct\MyAreaPath"])]
```

Every *Prediction* contains:
- The work item types the prediction should be run for (["Epic"] / ["User Story", "Bug"])
- Whether the predictions is active (True/False)
- How far back in history (in days) the data should be taken in to account for the simulation (180, 90)
- What work item states states are considered "done" for the forecast (["Closed", "Resolved"], ["Closed"])
- What area path the items are in (multiple paths are possible)

**Notice:** Be aware that depending on your template your work item types and states can differ (e.g. you might have "Product Backlog Item" and "Done" instead of "User Story" and "Closed")

After you've configured the predictions you want, save the file and run the script.

### Arguments
- Organization Url: The url to your Azure DevOps Organization. **Mandatory**
- Personal Access Token: A token that has the Work Items Read & Write scope active. **Mandatory**
- ReleaseTag: Tag to identify items for which the *When* forecast should be run. *Optional*
- TargetDate: Date for which the *How Many* forecast should be run. *Optional*
- GoalTag: Tag to identify the teams current goal (e.g. Sprint Goal). If set, a *When* forecast will be run for those items. *Optional*
- IterationLength: Length of your iteration in days. If set, a *How Many* forecast will be run for the amount of days. *Optional*
- RemainingItems: If you want to forecast a fixed amount of items, then you can specify it using this parameter intstead of using a Tag to dynamically get the remaining items. This will **only** be taken into account if *ReleaseTag* is omitted. *Optional*

## Calculate Work Item Age
Let's you update the age of your work items on Azure DevOps according to the following formula: `(Today - Start Date) + 1`
where the Start Date is the day when the item was moved out of the "New" state.

You can do a trial run of the script (meaning that it won't update any fields on your Azure DevOps) as follows:
`python .\CalculateWorkItemAge.py --OrganizationUrl "https://dev.azure.com/huserben/" --TeamProject "WIA_Demo" --PersonalAccessToken "***********" --FieldName "Age" --TrialRun "True"`

If you are happy with the results you can change the it as follows to write the age:
`python .\CalculateWorkItemAge.py --OrganizationUrl "https://dev.azure.com/huserben/" --TeamProject "WIA_Demo" --PersonalAccessToken "***********" --FieldName "Age" --TrialRun "False"`

### Arguments
- Organization Url: The url to your Azure DevOps Organization
- Team Project: The name of the team project where your work items are located
- Personal Access Token: A token that has the Work Items Read & Write scope active
- Field Name: The name of the field that you want to write your data to. Can be a custom field or some existing

You can find existing field names by checking the following url: `https://dev.azure.com/{OrganizationUrl}/{TeamProject}/_apis/wit/fields?api-version=7.0`

For example for the above example: `https://dev.azure.com/huserben/WIA_Demo/_apis/wit/fields?api-version=7.0`

As an example, if you want to write the age data in to the "Story Points" field, start the script like this:
`python .\CalculateWorkItemAge.py --OrganizationUrl "https://dev.azure.com/huserben/" --TeamProject "WIA_Demo" --PersonalAccessToken "***********" --FieldName "Story Points" --TrialRun "False"`

## Pipeline Integration
You want to run this script on a regular base. As we humans tend to forget this, I propose that you leverage your Azure Pipelines for this. I've included a "sample" in *AzurePipeline.yaml* that shows how you can run the scripts from there.
Use and adjust as you see fit.
