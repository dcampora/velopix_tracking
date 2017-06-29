#!/usr/bin/python3

import event_model as em
import validator_lite as vl
import json

# Solutions
from graph_dfs import graph_dfs
from classical_solver import classical_solver
solutions = {}

# Get an event
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Get all tracks by using the classic method and print them
classical = classical_solver()
solutions["classic"] = classical.solve(event)

# Invoke some algorithm to solve it
dfs = graph_dfs(allowed_missing_sensor_hits=0)
solutions["dfs"] = dfs.solve(event)

# Validate the solutions
for k, v in iter(sorted(solutions.items())):
  print("%s method validation" % (k))
  vl.validate_print([json_data], [v])
  print()
  # print('RE long>5GeV, [0-1]:', vl.validate_efficiency([json_data], [dfs_tracks], 'long>5GeV'))
  # print('CF long>5GeV, [0-1]:', vl.validate_clone_fraction([json_data], [dfs_tracks], 'long>5GeV'))
  # print('GF of all tracks, [0-1]:', vl.validate_ghost_fraction([json_data], [dfs_tracks]))
