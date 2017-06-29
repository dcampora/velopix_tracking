#!/usr/bin/python3

import event_model as em
import validator_lite as vl
import json

# Solvers
from graph_dfs import graph_dfs
from classical_solver import classical_solver
solutions = {}

# Get an event
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

for s_number in range(0, event.number_of_sensors):
  event.sensors[s_number].z = event.sensors[s_number].hits()[0].z

# Solve with the classic method
classical = classical_solver()
solutions["classic"] = classical.solve(event)

# Solve with the DFS method
dfs = graph_dfs()
solutions["dfs"] = dfs.solve(event)

from visual.base import print_event_2d
print_event_2d(event, solutions["classic"], filename="classic_solution_xz.png")
print_event_2d(event, solutions["classic"], y=1, filename="classic_solution_yz.png")

print_event_2d(event, solutions["dfs"], filename="dfs_solution_xz.png", track_color=4)
print_event_2d(event, solutions["dfs"], y=1, filename="dfs_solution_yz.png", track_color=4)
