from time import localtime
from hashlib import md5,shake_256
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

def add_prefix(filename):
    prefix = shake_256(f"{localtime()}{filename}".encode('utf-8')).hexdigest(20)
    return f"{BASE_DIR}/static/images_ortho/{prefix}",prefix

def add_prefix2(filename):
    prefix = shake_256(f"{localtime()}{filename}".encode('utf-8')).hexdigest(20)
    return f"{BASE_DIR}/static/images_counting/{prefix}",prefix