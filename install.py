import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = [
    "xlrd",
    "requests",
    "numpy",
    "qiskit",
    "bs4",
    "scikit-learn",
    "pandas",
]

for package in packages:
    install(package)
