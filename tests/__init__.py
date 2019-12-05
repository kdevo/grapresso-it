import os
import sys

# Inject local project path
sys.path.insert(1, os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../grapresso"))
os.chdir(os.path.abspath(os.path.dirname(__file__)))
