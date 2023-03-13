# AzureDevOpsPythonScripts

## Install Prerequisites
Make sure you have python 3.x installed on your system and it's available via your PATH variable.

Then run `python -m pip install -r .\requirements.txt` from this directory to install the packages.

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
You want to run this script on a regular base. As we humans tend to forget this, I propose that you leverage your Azure Pipelines for this. I've included a "sample" in *AzurePipeline.yaml* that shows how you can run the script from there.
Use and adjust as you please.