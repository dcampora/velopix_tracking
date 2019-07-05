#!/usr/bin/python3

import event_model as em
import validator_lite as vl
import json
from visual.base import print_event_2d

# Solvers
from graph_dfs import graph_dfs
from classical_solver import classical_solver
from trie_search.search_by_triplet_trie import *

solutions = {}

# Get an event
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

print_event_2d(ev, all_tracks[0], filename="classic_solution_xz.png")
print_event_2d(ev, all_tracks[0], y=1, filename="classic_solution_yz.png")

"""
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

from visual.base import print_event_2d
print_event_2d(event, solutions["classic"], filename="classic_solution_xz.png")
print_event_2d(event, solutions["classic"], y=1, filename="classic_solution_yz.png")

print_event_2d(event, solutions["dfs"], filename="dfs_solution_xz.png", track_color=4)
print_event_2d(event, solutions["dfs"], y=1, filename="dfs_solution_yz.png", track_color=4)
"""
