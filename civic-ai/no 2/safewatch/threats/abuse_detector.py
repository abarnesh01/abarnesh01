import time
from typing import List, Dict, Any

class AbuseDetector:
    """
    Detects repeated abuse or long-term violent interactions.
    """
    def __init__(self, incident_window: int = 60, count_threshold: int = 3):
        self.incident_window = incident_window
        self.count_threshold = count_threshold
        # { (id1, id2): [timestamp, ...] }
        self.interaction_history: Dict[tuple, List[float]] = {}

    def detect(self, current_threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        threats = []
        current_time = time.time()
        
        # Look for aggressive interactions
        violent_events = [t for t in current_threats if t['type'] in ["FIGHT", "ASSAULT"]]
        
        for event in violent_events:
            if len(event['ids']) >= 2:
                pair = tuple(sorted(event['ids'][:2]))
                
                if pair not in self.interaction_history:
                    self.interaction_history[pair] = []
                
                self.interaction_history[pair].append(current_time)
                
                # Cleanup old events
                self.interaction_history[pair] = [t for t in self.interaction_history[pair] 
                                                  if current_time - t < self.incident_window]
                
                if len(self.interaction_history[pair]) >= self.count_threshold:
                    threats.append({
                        "type": "ABUSE",
                        "severity": "CRITICAL",
                        "confidence": 0.9,
                        "ids": list(pair),
                        "description": f"Repeated violent interactions detected between {pair[0]} and {pair[1]}"
                    })
                    
        return threats
