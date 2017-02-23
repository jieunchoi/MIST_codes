import os

try:
    __WORK_DIR__ = os.environ["MESAWORK_DIR"]
    __MISTGRID_DIR__ = os.environ["MIST_GRID_DIR"]
    __CODE_DIR__ = os.environ["MIST_CODE_DIR"]
    __STORAGE_DIR__ = os.environ["STORE_DIR"]
    __MAKE_ISOCH_DIR__ = os.environ["ISO_DIR"]
    __XA_CALC_DIR__ = os.environ["XA_CALC_DIR"]
except KeyError:
    raise ImportError("Check that you have the MESAWORK_DIR, XA_CALC_DIR, MIST_GRID_DIR, MIST_CODE_DIR, STORE_DIR, and ISO_DIR environment variables set")
