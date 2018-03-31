import re
from urllib.parse import urlparse
from datetime import datetime
from collections import defaultdict


def parse(ignore_files=False,
          ignore_urls=False,
          start_at=None,
          stop_at=None,
          request_type=None,
          ignore_www=False,
          slow_queries=False):
    if ignore_urls is False:
        ignore_urls = []

    with open('log.log') as log_file:
        log = log_file.readlines()

    log_pattern = re.compile('\[(?P<request_date>.+)\] '
                             '"(?P<request_type>.+) (?P<request>.+) (?P<protocol>.+)" '
                             '(?P<response_code>\d+) '
                             '(?P<response_time>\d+)\n')

    out_log = defaultdict(lambda: [0, 0])

    for line in log:
        match = re.match(log_pattern, line)
        if not match:
            continue
        match_dict = match.groupdict()

        log_url = urlparse(match_dict['request']).netloc + urlparse(match_dict['request']).path

        # по дате
        if start_at or stop_at:
            log_date = datetime.strptime(match_dict['request_date'], '%d/%b/%Y %H:%M:%S')
            if stop_at and log_date > stop_at:
                continue
            if start_at and log_date < start_at:
                continue

        # если есть определенный тип запроса
        if request_type:
            if request_type != match_dict['request_type']:
                continue

        # игнорировать файлы
        if ignore_files:
            log_request = urlparse(match_dict['request'])
            match_file = re.match('.+\.[^./]*$', log_request.path)
            if match_file:
                continue

        # игнорировать урлы
        if ignore_urls:
            if log_url in ignore_urls:
                continue

        # игнорировать www
        if ignore_www:
            log_host = urlparse(match_dict['request']).netloc
            if log_host.startswith('www.'):
                out_log[log_url[4:]][0] += 1
                continue

        # считаем то, что не подошло под условия
        out_log[log_url][0] += 1

        # считаем время
        out_log[log_url][1] += int(match_dict['response_time'])

    if slow_queries:
        sorted_out_log = sorted(out_log.items(), key=lambda i: i[1][1] // i[1][0], reverse=True)
        result = [element[1][1] // element[1][0] for element in sorted_out_log[:5]]
    else:
        sorted_out_log = sorted(out_log.items(), key=lambda i: i[1][0], reverse=True)
        result = [element[1][0] for element in sorted_out_log[:5]]

    return result
