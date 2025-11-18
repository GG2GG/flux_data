# run backend first
python main.py  

#if error FileNotFoundError: [Errno 2] No such file or directory: '/Users/ketakialoni/Public/flux_data/artifacts/logs/README.md'
mkdir artifacts/logs/
create a file : README.md

#run server for unity design in new terminal
python -m http.server 8001

#in unity app
open the folder ./flux_data/The Placement Gambit inside the app