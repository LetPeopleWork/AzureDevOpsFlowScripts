from datetime import datetime

class WorkItem:
    def __init__(self, id, title, type, state, tags, boardColumn, closedDate, state_changed_date, area_path, iteration_path):
        self.id = id
        self.title = title.replace("'", "")
        self.type = type
        self.state = state
        self.tags = tags
        self.boardColumn = boardColumn
        self.area_path = area_path
        self.iteration_path = iteration_path
        
        if closedDate == "N/A":
            self.closedDate = None
        else:        
            self.closedDate = closedDate
            
        if state_changed_date == "N/A":
            self.state_changed_date = None
        else:
            self.state_changed_date = state_changed_date
            
    def parse_ado_date(self, date):
        try:
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        
    def contains_tag(self, tag):
        for existing_tag in self.tags.split(";"):
            if tag == existing_tag.strip():
                return True
        
        return False
            
    def to_dict(self):
            if self.closedDate != None:
                parsed_closed_date = self.parse_ado_date(self.closedDate)
            else:
                parsed_closed_date = datetime.min
                
            if self.state_changed_date != None:
                parsed_state_changed = self.parse_ado_date(self.state_changed_date)
            else:
                parsed_state_changed = datetime.min
                
            return {
                'id': self.id,
                'title': self.title,
                'type': self.type,
                'state': self.state,
                'boardColumn': self.boardColumn,
                'closedDate': parsed_closed_date.date(),
                'state_changed_date': parsed_state_changed.date(),
            }