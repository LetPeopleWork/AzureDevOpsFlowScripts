import os

class Prediction:
    
    def __init__(self, work_item_types, run_prediction, relevant_history_in_days, done_states, area_paths):
        self.work_item_types = work_item_types
        self.run_prediction = run_prediction
        self.relevant_history_in_days = int(relevant_history_in_days)
        self.done_states = done_states
        self.area_paths = area_paths
        
        self.remaining_items = 0
        
        self.how_many_50 = 0
        self.how_many_85 = 0
        self.how_many_95 = 0
        
        self.when_50 = None
        self.when_85 = None
        self.when_95 = None
        
        self.target_date_likelyhood = None
        self.target_date = None