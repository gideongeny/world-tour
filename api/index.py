import os
import sys

# Add the project root directory to sys.path
# This ensures that 'app.py' (which is in the parent directory) can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
app.debug = False
