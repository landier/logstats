import argparse
import sys
from time import sleep
import collections
import datetime


DEFAULT_FILE = 'access.log'
TOPN_SECTIONS = 5
# In seconds
INTERVAL = 10
HIGH_TRAFFIC_PERIOD = 120
HIGH_TRAFFIC_THRESHOLD = 10


def main():
    parser = argparse.ArgumentParser(description='Analyse HTTP logs')
    parser.add_argument('--file', '-f', default=DEFAULT_FILE, type=str, help='access log file')
    parser.add_argument('--threshold', '-t', default=HIGH_TRAFFIC_THRESHOLD, type=str, help='threshold for high traffic warning (nb of requests /second)')
    args = parser.parse_args()
    loop(args)


class IntervalStats:
    @staticmethod
    def parse_log_line(raw_line):
        # Should be a regex here to properly manage log format and not rely strictly on - separator and such
        return (raw_line.split('-')[3][5:].strip(),  # path
                raw_line.split('-')[4][1:4].strip()) # status code

    def __init__(self, raw_logs):
        clean_logs = list(map(self.parse_log_line, raw_logs))
        self.nb_requests = len(clean_logs)
        self.nb_requests_per_section = self.aggregate_logs_per_section(clean_logs)
        self.nb_requests_per_status = self.aggregate_logs_per_status(clean_logs)

    def aggregate_logs_per_status(self, logs):
        status_logs = map(lambda l: l[1], logs)
        return collections.Counter(status_logs)

    def aggregate_logs_per_section(self, logs):
        section_logs = map(lambda l: l[0].split('/')[1], logs)
        return collections.Counter(section_logs)


class OverallStats:
    def __init__(self):
        self.nb_requests = 0
        self.nb_requests_per_section = None
        self.nb_requests_per_status = None

    def update(self, last_stats: IntervalStats):
        self.nb_requests += last_stats.nb_requests
        if self.nb_requests_per_section is None:
            self.nb_requests_per_section = last_stats.nb_requests_per_section
        else:
            self.nb_requests_per_section += last_stats.nb_requests_per_section
        if self.nb_requests_per_status is None:
            self.nb_requests_per_status = last_stats.nb_requests_per_status
        else:
            self.nb_requests_per_status += last_stats.nb_requests_per_status

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


def display_stats(stats):
    header = f"\t|\trequests\t|"
    requests = f"\t|\t{stats.nb_requests}\t\t|"

    for status_code, nb_requests in stats.nb_requests_per_status.items():
        header += f"\t{status_code}\t|"
        requests += f"\t{nb_requests}\t|"
    
    sections = f"\tTop 5 more requested sections"
    for section, nb_requests in stats.nb_requests_per_section.most_common(TOPN_SECTIONS):
        sections += f"\n\t\t- {section} ({nb_requests})"

    print(header)
    print(requests)
    print("\n")
    print(sections)


def loop(args):
    all_stats = OverallStats()
    high_traffic_watcher = HighTrafficWatcher(args.threshold)
    t = 0
    
    with open(args.file, 'r+') as file:
        while True:
            try:
                raw_logs_lines = file.readlines()
                interval_stats = IntervalStats(raw_logs_lines)

                print(f"Elapsed time: {t} seconds", file=sys.stderr)
                print(f"\nStats between {t} and {t+INTERVAL} seconds")
                display_stats(interval_stats)
                print("\n")
                
                high_traffic_watcher.add_measure(interval_stats.nb_requests)

                all_stats.update(interval_stats)

                sleep(INTERVAL)
                t += INTERVAL
            except KeyboardInterrupt:
                print("Halting...")
                print("\nAll stats")
                display_stats(all_stats)
                sys.exit(0)


if __name__ == '__main__':
    main()
