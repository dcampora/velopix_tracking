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

# Solve with the classic method
classical = classical_solver()
solutions["classic"] = classical.solve(event)

# Solve with the DFS method
dfs = graph_dfs()
solutions["dfs"] = dfs.solve(event)

# Validate the solutions
for k, v in iter(sorted(solutions.items())):
  print("%s method validation" % (k))
  vl.validate_print([json_data], [v])
  print()
