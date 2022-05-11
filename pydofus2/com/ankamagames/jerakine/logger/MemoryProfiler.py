import linecache
import os
import sys
import tracemalloc


class MemoryProfiler:
    def logMemoryUsage(snapshot, key_type="lineno", limit=20, logfile="./log/memory_usage.log"):
        original_stdout = sys.stdout
        format_row = "{:<7} {:<50} {:<80} {:>10}"
        with open(logfile, "a") as fp:
            sys.stdout = fp
            print("#" + "*" * 100)
            print(format_row.format(*["index", "file", "line", "usage (mb)"]))
            snapshot = snapshot.filter_traces(
                (
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
                    tracemalloc.Filter(False, "<unknown>"),
                )
            )
            top_stats = snapshot.statistics(key_type)
            for index, stat in enumerate(top_stats[:limit], 1):
                frame = stat.traceback[0]
                filename = os.sep.join(frame.filename.split(os.sep)[-2:])
                line = linecache.getline(frame.filename, frame.lineno).strip()
                print(
                    format_row.format(
                        *[index, filename + ":" + str(frame.lineno), line, str(round(stat.size / (1024 * 1024), 2))]
                    )
                )
            other = top_stats[limit:]
            if other:
                size = sum(stat.size for stat in other)
                print("%s other: %.1f MB" % (len(other), size / (1024 * 1024)))
            total = sum(stat.size for stat in top_stats)
            print("Total allocated size: %.1f NB" % (total / (1024 * 1024)))
            sys.stdout = original_stdout
