from Classes.WorkItem import WorkItem
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import Wiql
from collections import deque

class WorkItemService:    
    
    def __init__(self, org_url, token):
        credentials = BasicAuthentication('', token)
        
        self.organization_url = org_url
        self.personal_access_token = token
        
        self.header_patch = {'Content-Type': 'application/json-patch+json'}
        
        self.connection = Connection(base_url=org_url, creds=credentials)
        self.wit_client = self.connection.clients.get_work_item_tracking_client()
    
    def get_items_via_wiql(self, wiql):
        wiql_results = self.wit_client.query_by_wiql(wiql).work_items

        if wiql_results:
            work_items = (self.wit_client.get_work_item(int(res.id), expand='Relations') for res in wiql_results)
            return work_items
        else:
            return []
    

    def get_items_by_tag(self, tag):
        wiql = Wiql(
                query="""
                select [System.Id]
                from WorkItems
                where [System.Tags] contains '{0}' """
            .format(tag)
            )

        return self.get_items_via_wiql(wiql)
        
    def get_items_by_area_path(self, work_item_type, area_path, starting_date = None):
        
        starting_date_statement = ""
        if starting_date:
            starting_date_statement = "AND [System.ChangedDate] >= '{0}'".format(starting_date)
        
        wiql = Wiql(
                query="""
                select [System.Id]
                from WorkItems
                where [System.WorkItemType] = '{0}'
                and [System.AreaPath] under '{1}'
                {2}"""
            .format(work_item_type, area_path, starting_date_statement)
            )

        return self.get_items_via_wiql(wiql)
        
    
    def get_open_items_by_tag(self, tag):
        work_items = []
        for wiql_result in self.get_items_by_tag(tag):
                work_item = self.convert_to_work_item(wiql_result)
                
                if work_item.state != "Closed" and work_item.state != "Done":
                    work_items.append(work_item)
                    
        return work_items
       
       
    def get_items_by_area_paths(self, work_item_types, area_paths, excluded_tags = [], starting_date = None):
        print("Getting work items of type {0} and within area paths {1} - This might take a while".format(work_item_types, area_paths))
        work_items = []
        
        for area_path in area_paths:
            for work_item_type in work_item_types:
                for wiql_result in self.get_items_by_area_path(work_item_type, area_path, starting_date):
                    work_item = self.convert_to_work_item(wiql_result)
                    
                    skip_work_item = False
                    
                    for excluded_tag in excluded_tags:
                        if work_item.contains_tag(excluded_tag):
                            skip_work_item = True
                            break
                    
                    if not skip_work_item:
                        work_items.append(work_item)
        
        return work_items
   

    def convert_to_work_item(self, wiql_result):
        type = "N/A"
        if 'System.WorkItemType' in wiql_result.fields:
            type = wiql_result.fields["System.WorkItemType"]
        title = "N/A"
        if 'System.Title' in wiql_result.fields:
            title = wiql_result.fields["System.Title"]
        state = "N/A"
        if 'System.State' in wiql_result.fields:
            state = wiql_result.fields["System.State"]
        tags = "N/A"
        if 'System.Tags' in wiql_result.fields:
            tags = wiql_result.fields["System.Tags"]
        boardColumn = "N/A"
        if 'System.BoardColumn' in wiql_result.fields:
            boardColumn = wiql_result.fields["System.BoardColumn"]
        boardColumnDone = "N/A"
        if 'System.BoardColumnDone' in wiql_result.fields:
            boardColumnDone = wiql_result.fields["System.BoardColumnDone"]
            
            if boardColumnDone:
                boardColumn += " Done"
        closedDate = "N/A"
        if 'Microsoft.VSTS.Common.ClosedDate' in wiql_result.fields:
            closedDate = wiql_result.fields["Microsoft.VSTS.Common.ClosedDate"]
        
        state_changed_date = "N/A"
        if "Microsoft.VSTS.Common.StateChangeDate" in wiql_result.fields:
            state_changed_date = wiql_result.fields["Microsoft.VSTS.Common.StateChangeDate"]            
            
        area_path = wiql_result.fields["System.AreaPath"]       
        iteration_path = wiql_result.fields["System.IterationPath"]
        
        return WorkItem(wiql_result.id, title, type, state, tags, boardColumn, closedDate, state_changed_date, area_path, iteration_path)

