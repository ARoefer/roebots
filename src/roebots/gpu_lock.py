import os
import time
import fcntl
import torch


class GPULock:
    def __init__(self, gpu_ids=None, lock_dir="/tmp/gpu_locks"):
        """
        Args:
            gpu_ids:  List of GPU IDs to choose from, e.g. [0, 2, 3].
                      Defaults to all available GPUs.
            lock_dir: Directory to store lock files.
        """
        if gpu_ids is None:
            gpu_ids = list(range(torch.cuda.device_count()))
        self.gpu_ids = gpu_ids
        self.lock_dir = lock_dir
        os.makedirs(lock_dir, exist_ok=True)

        self._lock_file = None
        self.device = None

    def acquire(self, poll_interval=5, timeout=None):
        """
        Block until a GPU is free, then claim it.

        Args:
            poll_interval: Seconds to wait between retries when all GPUs are busy.
            timeout:       Maximum seconds to wait before raising TimeoutError.
                           None means wait forever.

        Returns:
            device string, e.g. "cuda:2"

        Raises:
            TimeoutError: If no GPU becomes available within the timeout period.
        """
        deadline = time.monotonic() + timeout if timeout is not None else None

        while True:
            for gpu_id in self.gpu_ids:
                lock_path = os.path.join(self.lock_dir, f"gpu_{gpu_id}.lock")
                lock_file = open(lock_path, "w")
                try:
                    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self._lock_file = lock_file
                    self.device = f"cuda:{gpu_id}"
                    print(f"[GPULock] Acquired {self.device}")
                    return self.device
                except BlockingIOError:
                    lock_file.close()

            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Could not acquire a GPU lock within {timeout}s "
                    f"(tried GPUs: {self.gpu_ids})"
                )

            print(f"[GPULock] All GPUs busy, retrying in {poll_interval}s...")
            time.sleep(poll_interval)

    def release(self):
        """Release the currently held GPU lock."""
        if self._lock_file is not None:
            print(f"[GPULock] Releasing {self.device}")
            fcntl.flock(self._lock_file, fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None
            self.device = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False  # Don't suppress exceptions
