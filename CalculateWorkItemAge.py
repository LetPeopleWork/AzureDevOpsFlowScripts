from msrest.authentication import BasicAuthentication
from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking.models import Wiql
from datetime import date, datetime

import argparse
import requests
import json


parser = argparse.ArgumentParser()
parser.add_argument("--OrganizationUrl")
parser.add_argument("--TeamProject")
parser.add_argument("--PersonalAccessToken")
parser.add_argument("--FieldName")
parser.add_argument("--TrialRun")

args = parser.parse_args()

trial_run = args.TrialRun.upper() == "TRUE"
date_today = date.today()

## Setup ADO Connection
credentials = BasicAuthentication('', args.PersonalAccessToken)
connection = Connection(base_url=args.OrganizationUrl, creds=credentials)
wit_client = connection.clients.get_work_item_tracking_client()
header_patch = {'Content-Type': 'application/json-patch+json'}

def parse_ado_date(date):
    try:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")


def extract_age(work_item_history):
    for history_entry in work_item_history["value"]:
        if "fields" in history_entry and "System.State" in history_entry["fields"]:
            state_change = history_entry["fields"]["System.State"]
            changed_date_field = history_entry["fields"]["System.ChangedDate"]

            if "oldValue" in state_change and "newValue" in changed_date_field:
                old_state = state_change["oldValue"]
                new_state = state_change["newValue"]
                changed_date = parse_ado_date(changed_date_field["newValue"])

                # When it was moved "out of new" we care -> count days from then till today + 1 -> that's our WIA
                if old_state == "New":
                    
                    work_item_age = (date_today - changed_date.date()).days + 1
                    print("Item was moved from {0} to {1} on {2} -> Work Item Age: {3}".format(old_state, new_state, changed_date, work_item_age))
                    return work_item_age
                    
                    

    return 0

def get_items_via_wiql(wiql):
    wiql_results = wit_client.query_by_wiql(wiql).work_items

    if wiql_results:
        work_items = (wit_client.get_work_item(int(res.id), expand='Relations') for res in wiql_results)
        return work_items
    else:
        return []

def get_items_by_state(state, additional_condition=""):
    wiql = Wiql(
    query="""
            select [System.Id]
            from WorkItems
            where
                [System.TeamProject] = '{0}'
                and ([System.WorkItemType] = 'Bug' or [System.WorkItemType] = 'User Story')
                and [System.State] = '{1}'
                {2}"""
    .format(args.TeamProject, state, additional_condition)
    )

    return get_items_via_wiql(wiql)

def get_work_item_history(work_item_id):
    url_work_item_history = '{}/{}/_apis/wit/workItems/{}/updates?api-version=6.0'.format(args.OrganizationUrl, args.TeamProject, work_item_id)
    
    response = requests.get(url = url_work_item_history, headers=header_patch, auth=("", args.PersonalAccessToken))
    return json.loads(response.text)
    
def patch_work_item_field(work_item_id, field_name, field_value):
        data =  [
                    {
                    "op": "replace",
                    "path": "/fields/{}".format(field_name),
                    "value": field_value
                    }
                ]
        
        url_patch_workitem_state = '{}/{}/_apis/wit/workitems/{}?$expand=all&api-version=6.0'.format(args.OrganizationUrl, args.TeamProject, work_item_id)
            
        requests.patch(url=url_patch_workitem_state, json = data, headers = header_patch, auth=("", args.PersonalAccessToken))

def get_relevant_items():

    work_item_ids = []

    for active_item in get_items_by_state("Active"):
        work_item_ids.append(active_item.id)

    for resolved_item in get_items_by_state("Resolved"):
        work_item_ids.append(resolved_item.id)

    date_today = date.today()

    for closed_item in get_items_by_state("Closed", "and [Microsoft.VSTS.Common.ClosedDate] = '{0} 00:00:00Z'".format(date_today.strftime("%m/%d/%Y"))):
        work_item_ids.append(closed_item.id)

    return work_item_ids


def update_work_item_age():
    if trial_run:
        print("Trial Run flag is set - will not actually update the items...")

    work_item_ids = get_relevant_items()

    for work_item_id in work_item_ids:
        print("Checking Item {0}".format(work_item_id))
        work_item_history = get_work_item_history(work_item_id)
        work_item_age = extract_age(work_item_history)

        print("Item {0} is in progress since {1} days".format(work_item_id, work_item_age))

        if trial_run == False:
            patch_work_item_field(work_item_id, args.FieldName, work_item_age)


if __name__ == "__main__":
    update_work_item_age()
