
import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    print("Attempting: from backend.routers import planning")
    from backend.routers import planning
    print("Success: backend.routers.planning")
except ImportError as e:
    print(f"Failed backend.routers.planning: {e}")

try:
    print("Attempting: from routers import planning")
    from routers import planning
    print("Success: routers.planning")
except ImportError as e:
    print(f"Failed routers.planning: {e}")
