import os
import sys

# Add the AI_Land_Registry subdirectory to Python's path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, 'AI_Land_Registry'))

# Delegate execution to the subfolder's run script
if __name__ == '__main__':
    from AI_Land_Registry import run
