import argparse
import sys
from time import sleep

from stats import IntervalStats, OverallStats
from settings import DEFAULT_FILE, HIGH_TRAFFIC_THRESHOLD, TOPN_SECTIONS, INTERVAL
from watcher import HighTrafficWatcher


def main():
    parser = argparse.ArgumentParser(description='Analyse HTTP logs')
    parser.add_argument('--file', '-f', default=DEFAULT_FILE, type=str, help='access log file')
    parser.add_argument('--interval', '-i', default=INTERVAL, type=int, help='interval in seconds to display stats')
    parser.add_argument('--threshold', '-t', default=HIGH_TRAFFIC_THRESHOLD, type=int, help='threshold for high traffic warning (nb of requests /second)')
    args = parser.parse_args()
    loop(args)


def display_stats(elapsed_time, stats):
    header = f"time\t# requests\t"
    data = f"{elapsed_time}\t{stats.nb_requests}\t\t"

    # Number of requests and status codes
    for status_code, nb_requests in stats.nb_requests_per_status.items():
        header += f"\t# {status_code}"
        data += f"\t{nb_requests}"
    
    # Top 5 most visited sections
    header += "\t\tTop 5 most visited sections"
    data += "\t\t"
    for section, nb_requests in stats.nb_requests_per_section.most_common(TOPN_SECTIONS):
        data += f"/{section} ({nb_requests}), "

    print(header)
    print(data)
    print("\n")


def loop(args):
    all_stats = OverallStats()
    high_traffic_watcher = HighTrafficWatcher(args.threshold)
    t = 0
    
    with open(args.file, 'r+') as file:
        while True:
            try:
                raw_logs_lines = file.readlines()
                interval_stats = IntervalStats(raw_logs_lines)

                display_stats(t, interval_stats)
                
                high_traffic_watcher.add_measure(interval_stats.nb_requests)

                all_stats.update(interval_stats)

                sleep(args.interval)
                t += args.interval
            except KeyboardInterrupt:
                print("Halting...")
                print("\nAll stats")
                display_stats(all_stats)
                sys.exit(0)


if __name__ == '__main__':
    main()
