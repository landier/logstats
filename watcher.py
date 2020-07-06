import datetime
from settings import INTERVAL, HIGH_TRAFFIC_PERIOD


class HighTrafficWatcher:
    def __init__(self, threshold):
        self.threshold = threshold
        # Measures store numbers of requests for the last x intervals
        # x is determined automatically based on INTERVAL and HIGH_TRAFFIC_PERIOD
        self.measures = []
        self.total_measures = 0
        self._nb_of_measures = HIGH_TRAFFIC_PERIOD / INTERVAL
        self.alert_triggered = False

    def add_measure(self, new_measure):
        if len(self.measures) == self._nb_of_measures:
            self.total_measures -= self.measures.pop(0)
        self.measures.append(new_measure)
        self.total_measures += new_measure
        self.check()

    def check(self):
        if self.total_measures/(self._nb_of_measures*INTERVAL) > self.threshold:
            self.alert_triggered = True
            time = datetime.datetime.now().time()
            print(f"High traffic generated an alert - hits = {self.total_measures/(self._nb_of_measures*INTERVAL)}, triggered at {time}", file=sys.stderr)
        
        if self.alert_triggered == True and self.total_measures/(self._nb_of_measures*INTERVAL) < self.threshold:
            self.alert_triggered = False
            time = datetime.datetime.now().time()
            print(f"Traffic back to normal - hits = {self.total_measures/(self._nb_of_measures*INTERVAL)}, triggered at {time}", file=sys.stderr)
