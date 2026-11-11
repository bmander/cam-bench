"""The harness's measurer: it starts each runner and waits for it, from a process that holds next to
nothing, so that the operating system's account of the runner's peak memory is the runner's own.

On Linux a process's peak resident set starts at the peak of the process that started it: a
runner started by the harness itself would have whatever the harness holds (every height map it has
read) counted as its own. This process holds only Python itself, and starts every runner for the
harness (harness/run.py starts it, `python3 -I -S harness/measure.py`).

It reads requests from its standard input, one line of JSON each:

    {"argv": [...], "cwd": "...", "env": {...}, "stdout": PATH, "stderr": PATH,
     "timeout": SECONDS, "core": N or null}

starts `argv` in `cwd` with `env`, its output to the two files and nothing on its input, and only
on core `core` if one is given; kills it if it runs past `timeout`; and answers one line of JSON:

    {"code": its exit code, or null if it ran out of time,
     "seconds": wall-clock, from starting it to its exit,
     "cpu": user and system seconds, of every thread of it and of the children it waited for,
     "peak_bytes": the most it held resident at once}

or {"error": "..."} if it could not be started. Standard library only; Linux and macOS.
"""
import json
import os
import signal
import sys
import time

# ru_maxrss is in kibibytes on Linux, in bytes on macOS
MAXRSS_BYTES = 1 if sys.platform == "darwin" else 1024
# the signals Python ignores, which a runner should not inherit ignored (as subprocess resets them)
RESET = [getattr(signal, s) for s in ("SIGPIPE", "SIGXFZ", "SIGXFSZ") if hasattr(signal, s)]


def lower_peak():
    """Bring this process's own peak down to what it holds now (Linux): it is where a runner's
    peak starts."""
    try:
        with open("/proc/self/clear_refs", "w") as f:
            f.write("5")
    except OSError:
        pass


def run(req):
    os.chdir(req["cwd"])
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    out = os.open(req["stdout"], flags, 0o600)
    err = os.open(req["stderr"], flags, 0o600)
    null = os.open(os.devnull, os.O_RDONLY)
    actions = [(os.POSIX_SPAWN_DUP2, null, 0), (os.POSIX_SPAWN_DUP2, out, 1),
               (os.POSIX_SPAWN_DUP2, err, 2)]
    core = req.get("core")
    before = os.sched_getaffinity(0) if core is not None else None
    try:
        # a child takes its affinity from the process that starts it: pinned for the start only
        if core is not None:
            os.sched_setaffinity(0, {core})
        lower_peak()
        start = time.monotonic()
        pid = os.posix_spawnp(req["argv"][0], req["argv"], req["env"], file_actions=actions,
                              setsigdef=RESET)
    except OSError as e:
        return {"error": f"{req['argv'][0]}: {e.strerror or e}"}
    finally:
        if before is not None:
            os.sched_setaffinity(0, before)
        for fd in (out, err, null):
            os.close(fd)

    killed, reaped = [], None

    def ran_out(signum, frame):
        killed.append(True)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    signal.signal(signal.SIGALRM, ran_out)
    signal.setitimer(signal.ITIMER_REAL, req["timeout"])
    try:
        # wait for it to exit without reaping it: until it is reaped its pid is not reused, so a
        # timer that fires late kills only the exited process, which is harmless (no waitid on
        # macOS before Python 3.13: there wait4 reaps it at once)
        if hasattr(os, "waitid"):
            os.waitid(os.P_PID, pid, os.WEXITED | os.WNOWAIT)
        else:
            reaped = os.wait4(pid, 0)
        seconds = time.monotonic() - start
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
    _, status, usage = reaped or os.wait4(pid, 0)
    # ran out of time only if the timer's kill is what ended it, not an exit just before it
    timed_out = (killed and os.WIFSIGNALED(status)
                 and os.WTERMSIG(status) == signal.SIGKILL)
    return {"code": None if timed_out else os.waitstatus_to_exitcode(status),
            "seconds": seconds, "cpu": usage.ru_utime + usage.ru_stime,
            "peak_bytes": usage.ru_maxrss * MAXRSS_BYTES}


def main():
    for line in sys.stdin:
        if line.strip():
            sys.stdout.write(json.dumps(run(json.loads(line))) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
