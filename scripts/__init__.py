import os

try:
    __WORK_DIR__ = os.environ["MESAWORK_DIR"]
    __MISTGRID_DIR__ = os.environ["MIST_GRID_DIR"]
    __CODE_DIR__ = os.environ["MIST_CODE_DIR"]
    __STORAGE_DIR__ = os.environ["STORE_DIR"]
except KeyError:
    raise ImportError("Check that you have the MESAWORK_DIR, MIST_GRID_DIR, MIST_CODE_DIR, and STORE_DIR environment variables set")
