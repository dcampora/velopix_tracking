#!/usr/bin/python3

import json
import os
from event_model import event_model as em
from event_model.restricted_event_model import restrict_event
from validator import validator_lite as vl

# Solvers
from algorithms.track_following import track_following

solutions = {
  "track_following": []
}
validation_data = []

restrict_consec_modules = True
restrict_min_nb_hits = 3
restricted_modules = [0, 2, 4, 6]

# Instantiate algorithm
track_following = track_following()

# Iterate all events
for (dirpath, dirnames, filenames) in os.walk("events"):
  for i, filename in enumerate(filenames):
    # Get an event
    f = open(os.path.realpath(os.path.join(dirpath, filename)))
    event, json_data = restrict_event(json.loads(f.read()), restricted_modules, restrict_min_nb_hits, restrict_consec_modules)
    f.close()

    # Do track reconstruction
    print("Reconstructing event %i..." % (i))
    tracks = track_following.solve(event)

    # Append the solution and json_data
    solutions["track_following"].append(tracks)
    validation_data.append(json_data)

# Validate the solutions
for k, v in iter(sorted(solutions.items())):
  print("\nValidating tracks from %s:" % (k))
  vl.validate_print(validation_data, v)
  print()
