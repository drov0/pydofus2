import linecache
import os
import sys
from time import perf_counter
import tracemalloc


class MemoryProfiler:
    LOGRATE = 1 / 60
    LAST_LOGGED = 0
    SAVED_PROFILES = dict()
    SHOW_LIMIT = 20
    SAVE_LIMIT = 20
    LOG_FILE = "./log/memory_usage.log"
    KEY_TYPE = "lineno"

    @classmethod
    def logMemoryUsage(cls, snapshot):
        now = perf_counter()
        if now - cls.LAST_LOGGED < 1 / cls.LOGRATE:
            return
        cls.LAST_LOGGED = now
        with open(cls.LOG_FILE, "a") as fp:
            format_row = "{:<7} {:<50} {:<80} {:>10}"
            fp.write("# " + "*" * 100 + "\n")
            fp.write(format_row.format(*["index", "file", "line", "usage (mb)"]) + "\n")
            snapshot = snapshot.filter_traces(
                (
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
                    tracemalloc.Filter(False, "<unknown>"),
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
                    tracemalloc.Filter(False, "<lib\linecache.py>"),
                )
            )
            top_stats = snapshot.statistics(cls.KEY_TYPE)
            for index, stat in enumerate(top_stats[: cls.SAVE_LIMIT], 1):
                frame = stat.traceback[0]
                filename = os.sep.join(frame.filename.split(os.sep)[-2:])
                line = linecache.getline(frame.filename, frame.lineno).strip()
                fileLine = filename + ":" + str(frame.lineno)
                usage = round(stat.size / (1024 * 1024), 2)
                if fileLine not in cls.SAVED_PROFILES:
                    cls.SAVED_PROFILES[fileLine] = []
                cls.SAVED_PROFILES[fileLine].append(usage)
                if index < cls.SHOW_LIMIT:
                    fp.write(format_row.format(*[index, fileLine, line, str(usage)]) + "\n")
            other = top_stats[cls.SAVE_LIMIT :]
            if other:
                if "other" not in cls.SAVED_PROFILES:
                    cls.SAVED_PROFILES["other"] = []
                size = sum(stat.size for stat in other) / (1024 * 1024)
                cls.SAVED_PROFILES["other"].append(size)
                fp.write("%s other: %.1f MB" % (len(other), size) + "\n")
            total = sum(stat.size for stat in top_stats)
            fp.write("Total allocated size: %.1f NB" % (total / (1024 * 1024)) + "\n")

    @classmethod
    def saveCollectedData(cls):
        import csv
        import datetime

        now = datetime.datetime.now()
        fieldnames = list(cls.SAVED_PROFILES.keys())
        with open(f"./log/stats/MemoryStats-{now.strftime('%Y-%m-%d')}.csv", "w") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cls.SAVED_PROFILES)
