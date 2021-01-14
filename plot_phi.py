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

for s_number in range(0, event.number_of_modules):
  event.modules[s_number].z = event.modules[s_number].hits()[0].z

# Solve with the classic method
classical = classical_solver()
solutions["classic"] = classical.solve(event)

# Solve with the DFS method
dfs = graph_dfs(
  allow_cross_track=False,
  allowed_skip_modules=1,
  max_slopes=(0.7, 0.7),
  max_tolerance=(0.3, 0.3)
)
solutions["dfs"] = dfs.solve(event)

from visual.print_phi import print_event_2d_phi
print_event_2d_phi(event, solutions["classic"], filename="event_phi")
