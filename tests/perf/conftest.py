# The following has essentially been adapted from https://pypi.org/project/pytest-memprof/0.2.0

import threading

import psutil
# import pandas
import pytest
import time


def pytest_addoption(parser):
    group = parser.getgroup('memprof')
    group.addoption(
        '--memprof-top-n',
        action='store',
        dest='memprof_top_n',
        default=0,
        help='limit memory reports to top n entries, report all if value is 0',
    )

    # group.addoption(
    #     '--profiling-csv-file',
    #     action='store',
    #     dest='csv_file',
    #     default=None,
    #     help='Output comma separated value table to given filename',
    # )

    parser.addini('memprof_top_n', 'limit memory reports to top n entries')
    # parser.addini('memprof_csv_file', 'output comma separated value table to given filename')


mem_consumptions = {}
time_consumptions = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    def available_mem():
        return psutil.virtual_memory().available

    before = available_mem()

    peaks = []
    running = threading.Event()
    running.set()

    def report_mem():
        peaks.append(available_mem())
        if running.is_set():
            # run this function in 0.1 seconds again:
            threading.Timer(0.1, report_mem).start()

    report_mem()

    start = time.time()
    yield
    end = time.time()
    duration = end - start

    running.clear()

    key = "::".join(item.listnames()[2:])

    after = min(peaks + [available_mem()])
    increase = before - after
    if increase > 0:
        mem_consumptions[key] = increase
        time_consumptions[key] = duration


def fmt_mem(mem):
    kb, b = divmod(mem, 1024)
    mb, kb = divmod(kb, 1024)
    if mb:
        return "%.1f MB" % (mem / 1024.0 / 1024.0)
    if kb:
        return "%.1f KB" % (mem / 1024.0)
    else:
        return "%.2f B" % mem


def fmt_duration(duration):
    return "%.2fs" % duration


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus):
    tr = terminalreporter

    top_n = tr.config.option.memprof_top_n
    # csv_filename = tr.config.option.memprof_csv_file

    try:
        top_n = int(top_n)
    except ValueError:
        raise ValueError("given parameter --memprof-top-n is no int")

    items = sorted(time_consumptions.items(), key=lambda item: -item[1])

    if top_n:
        items = items[:top_n]

    if items:
        tr.section("time/memory consumption estimates")
        numc = max([len(name) for name, value in items]) + 1
        filler = numc * " "
        for name, value in items:
            tr.write((name + filler)[:numc] + " - ")
            tr.write(fmt_duration(value), bold=True)
            tr.write(" / ")
            tr.write(fmt_mem(mem_consumptions[name]) + "\n", bold=True)

        # if csv_filename:
        #     with open(csv_filename, 'wt') as csvfile:
        #         writer = csv.writer(csvfile)
        #         writer.writerow(['function', 'memory'])
        #         writer.writerows(items)
    yield
