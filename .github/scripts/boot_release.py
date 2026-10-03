#!/usr/bin/env python3
"""Boot a release server in a temporary world and stop it through the console."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    env = os.environ.copy()
    env["RUST_LOG"] = "info"
    with tempfile.TemporaryDirectory(prefix="pumpkin-release-") as scratch:
        with args.log.open("w") as log:
            proc = subprocess.Popen(
                [str(binary)], cwd=scratch, env=env, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                bufsize=1,
            )
            lines: queue.Queue[str] = queue.Queue()

            def read_output() -> None:
                assert proc.stdout is not None
                for line in proc.stdout:
                    log.write(line)
                    log.flush()
                    lines.put(line)

            reader = threading.Thread(target=read_output, daemon=True)
            reader.start()
            started = False
            try:
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline and proc.poll() is None:
                    try:
                        line = lines.get(timeout=0.2)
                    except queue.Empty:
                        continue
                    if "Started server;" in line:
                        started = True
                        break
                assert proc.stdin is not None
                if proc.poll() is None:
                    proc.stdin.write("version\nstop\n")
                    proc.stdin.flush()
                proc.stdin.close()
                proc.wait(timeout=30)
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                reader.join(timeout=5)
            if not started or proc.returncode != 0:
                raise SystemExit(f"Release boot failed: started={started}, exit={proc.returncode}")
    contents = args.log.read_text()
    if "The server has stopped." not in contents or " ERROR" in contents or "panicked" in contents:
        raise SystemExit("Release did not shut down cleanly; inspect the boot log")
    print("Release startup and console shutdown passed")


if __name__ == "__main__":
    main()
