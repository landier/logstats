import collections


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
