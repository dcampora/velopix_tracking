import sys
sys.path.append("../")
from classical_solver import classical_solver
import validator_lite as vl
import json
from event_model import *

# Constants
max_scatter = 0.1

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

def check_scatter(h0, h1, h2):
  return calculate_scatter(h0, h1, h2) < max_scatter

def check_compatible_triplets(m0, m1, m2):
  compatible_triplets = []
  for h0 in m0.hits():
    for h1 in m1.hits():
      for h2 in m2.hits():
        if check_scatter(h0, h1, h2):
          compatible_triplets.append((h0, h1, h2))
  return compatible_triplets

def generate_compatible_triplets(event, consider_missing_layers=False, consider_both_sides=False):
  compatible_triplets_trie = {}
  for m0, m1 in zip(reversed(event.modules[4:]), reversed(event.modules[2:-2])):
    compatible_triplets_module = {}
    compatible_triplets = []

    if not consider_both_sides:
      m2 = m1.module_number - 2
      compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2])
      if m2 - 2 > 0 and consider_missing_layers:
        compatible_triplets += check_compatible_triplets(m0, event.modules[m2], event.modules[m2 - 2])
        compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2 - 2])
    else:
      # Verify m2 and m2 - 1
      m2 = (m1.module_number - (m1.module_number % 2)) - 1
      # Check compatible triplets
      compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2])
      compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2 - 1])
      if m2 - 2 > 0 and consider_missing_layers:
        compatible_triplets += check_compatible_triplets(m0, event.modules[m2], event.modules[m2 - 2])
        compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2 - 2])
        compatible_triplets += check_compatible_triplets(m0, event.modules[m2 - 1], event.modules[m2 - 3])
        compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2 - 3])

    # Iterate compatible_triplets and generate a trie from it
    for h0, h1, h2 in compatible_triplets:
      key = (h0, h1)
      if key not in compatible_triplets_module.keys():
        compatible_triplets_module[key] = [h2]
      else:
        compatible_triplets_module[key].append(h2)
    compatible_triplets_trie[m0.module_number] = compatible_triplets_module

  return compatible_triplets_trie

def generate_compatible_triplets_forwarding_missing(event):
  compatible_triplets_trie = {}
  for m1, m2 in zip(reversed(event.modules[2:-4]), reversed(event.modules[:-6])):
    compatible_triplets_module = {}
    compatible_triplets = []

    m0_prev = event.modules[m1.module_number + 4]
    m0 = event.modules[m1.module_number + 2]

    compatible_triplets += check_compatible_triplets(m0_prev, m0, m2)
    compatible_triplets += check_compatible_triplets(m0_prev, m1, m2)

    compatible_triplets_trie[m2.module_number] = compatible_triplets_module

  return compatible_triplets_trie

json_data_all_events = []
all_tracks = []

for event_number in range(0, 20):
  # Get an event
  f = open("../velojson/" + str(event_number) + ".json")
  json_data = json.loads(f.read())
  ev = event(json_data)
  f.close()

  # Build a trie with compatible triplets per module and hit pair
  compatible_triplets_trie = generate_compatible_triplets(ev)
  compatible_triplets_forwarding_missing_trie = generate_compatible_triplets_forwarding_missing(ev)

  flagged_hits = set()
  forwarding_tracks = []
  tracks = []
  weak_tracks = []

  # Use compatible triplets to find compatibility between hits (seeding)
  # and between tracks and hits (forwarding)
  # Even modules
  for m0, m1 in zip(reversed(ev.modules[4::2]), reversed(ev.modules[2:-2:2])):
    compatible_triplets_in_module = compatible_triplets_trie[m0.module_number]
    forwarding_next_step = []

    # Forwarding
    for t in forwarding_tracks:
      # Last two hits
      h0 = t.hits[-2]
      h1 = t.hits[-1]
      # Check if there are compatible hits
      found_h2 = False
      if (h0, h1) in compatible_triplets_in_module.keys():
        best_h2 = hit(0, 0, 0, -1)
        best_scatter = max_scatter
        compatible_h2s = compatible_triplets_in_module[(h0, h1)]
        for h2 in compatible_h2s:
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
          t.missed_modules = 0
      if not found_h2 and (h0, h1) in compatible_triplets_forwarding_missing_trie.keys():
        best_h2 = hit(0, 0, 0, -1)
        best_scatter = max_scatter
        compatible_h2s = compatible_triplets_in_module[(h0, h1)]
        for h2 in compatible_h2s:
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
          t.missed_modules = 0
      if not found_h2:
        t.missed_modules += 1
        if t.missed_modules > 1:
          if len(t.hits) > 3:
            tracks.append(t)
          else:
            weak_tracks.append(t)
        else:
          forwarding_next_step.append(t)

    forwarding_tracks = forwarding_next_step

    # Seeding
    for h0, h1 in compatible_triplets_in_module.keys():
      if h0 not in flagged_hits and h1 not in flagged_hits:
        best_h2 = hit(0, 0, 0, -1)
        best_scatter = max_scatter
        compatible_h2s = compatible_triplets_in_module[(h0, h1)]
        for h2 in compatible_h2s:
          scatter = calculate_scatter(h0, h1, h2)
          if h2 not in flagged_hits and scatter < best_scatter:
            best_h2 = h2
            best_scatter = scatter
        if best_h2.id != -1:
          forwarding_tracks.append(track([h0, h1, best_h2]))

  # Odd modules (note: code repeated)
  for m0, m1 in zip(reversed(ev.modules[5::2]), reversed(ev.modules[3:-2:2])):
    compatible_triplets_in_module = compatible_triplets_trie[m0.module_number]
    forwarding_next_step = []

    # Forwarding
    for t in forwarding_tracks:
      # Last two hits
      h0 = t.hits[-2]
      h1 = t.hits[-1]
      # Check if there are compatible hits
      found_h2 = False
      if (h0, h1) in compatible_triplets_in_module.keys():
        best_h2 = hit(0, 0, 0, -1)
        best_scatter = max_scatter
        compatible_h2s = compatible_triplets_in_module[(h0, h1)]
        for h2 in compatible_h2s:
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
          t.missed_modules = 0
      if not found_h2 and (h0, h1) in compatible_triplets_forwarding_missing_trie.keys():
        best_h2 = hit(0, 0, 0, -1)
        best_scatter = max_scatter
        compatible_h2s = compatible_triplets_in_module[(h0, h1)]
        for h2 in compatible_h2s:
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
          t.missed_modules = 0
      if not found_h2:
        t.missed_modules += 1
        if t.missed_modules > 1:
          if len(t.hits) > 3:
            tracks.append(t)
          else:
            weak_tracks.append(t)
        else:
          forwarding_next_step.append(t)

    forwarding_tracks = forwarding_next_step

    # Seeding
    for h0, h1 in compatible_triplets_in_module.keys():
      if h0 not in flagged_hits and h1 not in flagged_hits:
        best_h2 = hit(0, 0, 0, -1)
        best_scatter = max_scatter
        compatible_h2s = compatible_triplets_in_module[(h0, h1)]
        for h2 in compatible_h2s:
          scatter = calculate_scatter(h0, h1, h2)
          if h2 not in flagged_hits and scatter < best_scatter:
            best_h2 = h2
            best_scatter = scatter
        if best_h2.id != -1:
          forwarding_tracks.append(track([h0, h1, best_h2]))

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

vl.validate_print(json_data_all_events, all_tracks)
