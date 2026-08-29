import sys
import os
import warnings

# Suppress verbose TensorFlow / Mediapipe logs and specific protobuf warning
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
warnings.filterwarnings("ignore", message=".*SymbolDatabase.GetPrototype.*")

# Add project root and src/ to path for src-layout imports
ROOT = os.path.dirname(os.path.abspath(__file__))
for candidate in (ROOT, os.path.join(ROOT, "src")):
    if os.path.isdir(candidate):
        sys.path.insert(0, candidate)

from kids_athletics.top import main


if __name__ == "__main__":
    main()
