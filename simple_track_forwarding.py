from classical_solver import classical_solver
import event_model as em
import validator_lite as vl
import json

# Get an event
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Constants
max_slopes=(0.7, 0.7)
max_tolerance=(0.4, 0.4)
max_scatter=0.4

def generate_hit_list(event):
  for module in event.modules:
    for hit in module.hits():
      print("h" + str(hit.module_number) + "," + str(hit.id))

def print_compatible_triplet_simplified(triplet):
  h0, h1, h2 = triplet
  print(str(h0.id) + "," + str(h1.id) + "," + str(h2.id))

def print_compatible_triplet(triplet):
  h0, h1, h2 = triplet
  print("[" + \
    "h" + str(h0.module_number) + "," + str(h0.id) + ", " + \
    "h" + str(h1.module_number) + "," + str(h1.id) + ", " + \
    "h" + str(h2.module_number) + "," + str(h2.id) + \
    "] -> " + \
    "t" + str(h0.module_number) + "," + str(h0.id) + "," + str(h0.id) + ", " + \
    "t" + str(h1.module_number) + "," + str(h1.id) + "," + str(h0.id) + ", " + \
    "t" + str(h2.module_number) + "," + str(h2.id) + "," + str(h0.id) + \
    " []")

def print_compatible_forwarding_triplet(triplet):
  h0, h1, h2 = triplet
  print("[" + \
    "t" + str(h0.module_number) + "," + str(h0.id) + ",X, " + \
    "t" + str(h1.module_number) + "," + str(h1.id) + ",X, " + \
    "h" + str(h2.module_number) + "," + str(h2.id) + \
    "] -> " + \
    "t" + str(h0.module_number) + "," + str(h0.id) + ",X, " + \
    "t" + str(h1.module_number) + "," + str(h1.id) + ",X, " + \
    "t" + str(h2.module_number) + "," + str(h2.id) + ",X" + \
    " []")

def are_compatible(h0, h1):
  hit_distance = abs(h1.z - h0.z)
  dxmax = max_slopes[0] * hit_distance
  dymax = max_slopes[1] * hit_distance
  return abs(h1.x - h0.x) < dxmax and \
         abs(h1.y - h0.y) < dymax

def check_tolerance(h0, h1, h2):
  td = 1.0 / (h1.z - h0.z)
  txn = h1.x - h0.x
  tyn = h1.y - h0.y
  tx = txn * td
  ty = tyn * td

  dz = h2.z - h0.z
  x_prediction = h0.x + tx * dz
  dx = abs(x_prediction - h2.x)
  tolx_condition = dx < max_tolerance[0]

  y_prediction = h0.y + ty * dz
  dy = abs(y_prediction - h2.y)
  toly_condition = dy < max_tolerance[1]

  scatterNum = (dx * dx) + (dy * dy)
  scatterDenom = 1.0 / (h2.z - h1.z)
  scatter = scatterNum * scatterDenom * scatterDenom

  scatter_condition = scatter < max_scatter
  return tolx_condition and toly_condition and scatter_condition

def check_compatible_triplets(m0, m1, m2):
  compatible_triplets = []
  for h0 in m0.hits():
    for h1 in m1.hits():
      if are_compatible(h0, h1):
        for h2 in m2.hits():
          if check_tolerance(h0, h1, h2):
            compatible_triplets.append((h0, h1, h2))
  return compatible_triplets

def generate_compatible_triplets(event, consider_missing_layers=True):
  compatible_triplets = []
  for m0, m1 in zip(reversed(event.modules[4:]), reversed(event.modules[2:-2])):
    # Verify m2 and m2 - 1
    m2 = (m1.module_number - (m1.module_number % 2)) - 1
    # Check compatible triplets
    compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2])
    compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2 - 1])
    if m2 - 2 > 0 and consider_missing_layers:
      compatible_triplets += check_compatible_triplets(m0, event.modules[m2], event.modules[m2 - 2])
      compatible_triplets += check_compatible_triplets(m0, event.modules[m2 - 1], event.modules[m2 - 3])
      compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2 - 2])
      compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m2 - 3])
  
  generate_hit_list(event)

  print()
  for t in compatible_triplets:
    print_compatible_triplet_simplified(t)

generate_compatible_triplets(event)
