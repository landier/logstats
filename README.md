# Logstats

## Requirements
* Python 3.7.3 (tested)

## Instructions
```text
Write a simple program to monitor a given HTTP access log file and provide alerting and monitoring.

The program will consume an actively written-to w3c-formatted HTTP access log. It should default to reading /var/log/access.log and be overridable. Display stats every 10s about the traffic during those 10s: the sections of the web site with the most hits, as well as interesting summary statistics on the traffic as a whole. A section is defined as being what's before the second / in the path. For example, the section for http://my.site.com/pages/create is http://my.site.com/pages. Make sure a user can keep the app running and monitor the log file continuously. Whenever total traffic for the past 2 minutes exceeds a certain number on average, add a message saying that: "High traffic generated an alert - hits = {value}, triggered at {time}". The default threshold should be 10 requests per second and should be overridable. Whenever the total traffic drops again below that value on average for the past 2 minutes, print or displays another message detailing when the alert recovered.
```

## Help
```bash
python main.py -h
usage: main.py [-h] [--file FILE] [--interval INTERVAL] [--threshold THRESHOLD]

Analyse HTTP logs

optional arguments:
  -h, --help                            show this help message and exit
  --file FILE, -f FILE                  access log file
  --interval INTERVAL, -i INTERVAL      interval in seconds to display stats
  --threshold THRESHOLD, -t THRESHOLD   threshold for high traffic warning (nb of requests /second)
```

## TODO
[] Add tests :)
[] Regex for the log parsing
[] Add a log generator to ease test and debug
