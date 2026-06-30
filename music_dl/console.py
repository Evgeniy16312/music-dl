import threading

from rich.console import Console

console = Console(stderr=True)
print_lock = threading.Lock()
