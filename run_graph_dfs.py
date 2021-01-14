#!/usr/bin/python3

import json
from os import walk
from event_model import event_model as em
from event_model import validator_lite as vl

# Solvers
from algorithms.track_forwarding import track_forwarding
solutions = {}

# Instantiate algorithm
track_forwarding = track_forwarding()

# Iterate all events
for (dirpath, dirnames, filenames) in walk("events"):
# Get an event
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Solve with the classic method
solutions["classic"] = classical.solve(event)

# Validate the solutions
for k, v in iter(sorted(solutions.items())):
  print("%s method validation" % (k))
  vl.validate_print([json_data], [v])
  print()
