import sys
import os

# Add application directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from main import app as application
