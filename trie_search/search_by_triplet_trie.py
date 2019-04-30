import sys
sys.path.append("../")
from classical_solver import classical_solver
import validator_lite as vl
import json
from event_model import *

# Constants
max_scatter = 0.1

# Merge modules two by two
def merge_module_pairs(ev):
  module_pairs = []
  for m0, m1 in zip(ev.modules[0::2], ev.modules[1::2]):
    module_pairs.append(
      module(m0.module_number / 2,
      m0.z,
      m0.hit_start_index,
      m1.hit_end_index - m0.hit_start_index,
      m0._module__global_hits))
  return module_pairs

def calculate_scatter(h0, h1, h2):
  td = 1.0 / (h1.z - h0.z)
  txn = h1.x - h0.x
  tyn = h1.y - h0.y
  tx = txn * td
  ty = tyn * td

  dz = h2.z - h0.z
  x_prediction = h0.x + tx * dz
  y_prediction = h0.y + ty * dz
  dx = x_prediction - h2.x
  dy = y_prediction - h2.y

  return dx * dx + dy * dy

def check_best_triplets(m0, m1, m2):
  best_triplets = []
  for h0 in m0.hits():
    for h1 in m1.hits():
      best_h2 = hit(0, 0, 0, -1)
      best_scatter = max_scatter
      for h2 in m2.hits():
        scatter = calculate_scatter(h0, h1, h2)
        if scatter < best_scatter:
          best_h2 = h2
          best_scatter = scatter
      if best_scatter < max_scatter:
        best_triplets.append((h0, h1, best_h2))
  return best_triplets

def generate_compatible_triplets(module_pairs):
  compatible_triplets_trie = [None] * 26
  for m0, m1 in zip(reversed(module_pairs[2:]), reversed(module_pairs[1:-1])):
    compatible_triplets_module = {}
    compatible_triplets = []
    m2 = m1.module_number - 1
    compatible_triplets += check_best_triplets(m0, m1, module_pairs[m2])
    # Iterate compatible_triplets and generate a trie from it
    for h0, h1, h2 in compatible_triplets:
      if h0 not in compatible_triplets_module.keys():
        compatible_triplets_module[h0] = {}
      compatible_triplets_module[h0][h1] = h2
    compatible_triplets_trie[m0.module_number] = compatible_triplets_module
  return compatible_triplets_trie

json_data_all_events = []
all_tracks = []

print("Processing events", end="")
for event_number in range(0, 1):
  print(".", end="")
  sys.stdout.flush()
  # Get an event
  f = open("../velojson/" + str(event_number) + ".json")
  json_data = json.loads(f.read())
  ev = event(json_data)
  f.close()

  # Merge both module sides to simplify problem
  module_pairs = merge_module_pairs(ev)

  # Build a trie with compatible triplets per module and hit pair
  compatible_triplets_trie = generate_compatible_triplets(module_pairs)

  flagged_hits = set()
  forwarding_tracks = []
  tracks = []
  weak_tracks = []

  # Use compatible triplets to find compatibility between hits (seeding)
  # and between tracks and hits (forwarding)
  for m0, m1 in zip(reversed(module_pairs[2::1]), reversed(module_pairs[:-2:1])):
    compatible_triplets_in_module = compatible_triplets_trie[m0.module_number]
    forwarding_next_step = []

    # Forwarding
    for t in forwarding_tracks:
      # Last two hits
      h0 = t.hits[-2]
      h1 = t.hits[-1]
      # Check if there are compatible hits
      found_h2 = False
      if t.missed_last_module or t.missed_penultimate_module:
        # We missed a module
        # Let's try to find a compatible hit among all hits in the current processing module
        best_h2 = hit(0, 0, 0, -1)
        best_scatter = max_scatter
        hits_m2 = ev.modules[m1.module_number - 1].hits()
        for h2 in hits_m2:
          scatter = calculate_scatter(h0, h1, h2)
          if h2 not in flagged_hits and scatter < best_scatter:
            best_h2 = h2
            best_scatter = scatter
        if best_h2.id != -1:
          # Append and flag hits
          found_h2 = True
          t.hits.append(best_h2)
          flagged_hits.add(best_h2)
          if len(t.hits) == 4:
            flagged_hits.add(t.hits[0])
            flagged_hits.add(t.hits[1])
            flagged_hits.add(t.hits[2])
          forwarding_next_step.append(t)
          t.missed_penultimate_module = t.missed_last_module
          t.missed_last_module = False
      elif h0 in compatible_triplets_in_module.keys() and \
           h1 in compatible_triplets_in_module[h0].keys():
        h2 = compatible_triplets_in_module[h0][h1]
        # Append and flag hits
        found_h2 = True
        t.hits.append(h2)
        flagged_hits.add(h2)
        if len(t.hits) == 4:
          flagged_hits.add(t.hits[0])
          flagged_hits.add(t.hits[1])
          flagged_hits.add(t.hits[2])
        forwarding_next_step.append(t)
      if not found_h2:
        t.missed_penultimate_module = t.missed_last_module
        t.missed_last_module = True
        if t.missed_penultimate_module:
          if len(t.hits) > 3:
            tracks.append(t)
          else:
            weak_tracks.append(t)
        else:
          forwarding_next_step.append(t)

    forwarding_tracks = forwarding_next_step

    # Seeding
    for h0 in compatible_triplets_in_module.keys():
      for h1 in compatible_triplets_in_module[h0].keys():
        h2 = compatible_triplets_in_module[h0][h1]
        if h0 not in flagged_hits and \
           h1 not in flagged_hits and \
           h2 not in flagged_hits:
          forwarding_tracks.append(track([h0, h1, h2]))

  # Add tracks in forwarding_tracks to either tracks or weak_tracks container
  for t in forwarding_tracks:
    if len(t.hits) > 3:
      tracks.append(t)
    else:
      weak_tracks.append(t)

  # Finally process weak tracks
  for t in weak_tracks:
    if t.hits[0] not in flagged_hits and \
       t.hits[1] not in flagged_hits and \
       t.hits[2] not in flagged_hits:
       tracks.append(t)

  # Append to all events
  json_data_all_events.append(json_data)
  all_tracks.append(tracks)

print("\nValidating solution")
vl.validate_print(json_data_all_events, all_tracks)
