#!/usr/bin/python3

import event_model as em
import validator_lite as vl
import json

from graph_dfs import graph_dfs

# Get an event
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Invoke some algorithm to solve it
dfs = graph_dfs()
dfs_tracks = dfs.solve(event)

# # Get all tracks by using the classical method and print them
classical = classical_solver()
classical_tracks = classical.solve(event)

# Validate the event
vl.validate_print([json_data], [dfs_tracks])
print('RE long>5GeV, [0-1]:', vl.validate_efficiency([json_data], [dfs_tracks], 'long>5GeV'))
print('CF long>5GeV, [0-1]:', vl.validate_clone_fraction([json_data], [dfs_tracks], 'long>5GeV'))
print('GF of all tracks, [0-1]:', vl.validate_ghost_fraction([json_data], [dfs_tracks]))
