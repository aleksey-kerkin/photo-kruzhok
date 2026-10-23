import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ["USE_SQLITE"] = "1"
