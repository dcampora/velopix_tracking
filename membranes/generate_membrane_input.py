import sys
sys.path.append("../")
from classical_solver import classical_solver
import event_model as em
import validator_lite as vl
import json

# Get an event
f = open("../velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Constants
max_scatter = 0.1

# Output files
output_filename_prefix = "../"
hit_list_filename = output_filename_prefix + "velopix_hit_list.csv"
compatible_triplets_seeding_filename = output_filename_prefix + "velopix_compatible_triplets_seeding.csv"
compatible_triplets_forwarding_filename = output_filename_prefix + "velopix_compatible_triplets_forwarding.csv"

def generate_hit_list(event, output_file):
  for module in event.modules:
    for hit in module.hits():
      output_file.write("h" + str(hit.module_number) + "," + str(hit.id) + "\n")

def print_compatible_triplet_simplified(triplet, output_file):
  h0, h1, h2 = triplet
  output_file.write(str(h0.id) + "," + str(h1.id) + "," + str(h2.id) + "\n")

def check_tolerance(h0, h1, h2):
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

  return dx * dx + dy * dy < max_scatter

def check_compatible_triplets(m0, m1, m2):
  compatible_triplets = []
  for h0 in m0.hits():
    for h1 in m1.hits():
      for h2 in m2.hits():
        if check_tolerance(h0, h1, h2):
          compatible_triplets.append((h0, h1, h2))
  return compatible_triplets

def generate_compatible_triplets(event, output_file, seeding=False, consider_missing_layers=True):
  compatible_triplets = []
  for m0, m1 in zip(reversed(event.modules[4:]), reversed(event.modules[2:-2])):
    if seeding:
      # Only generate compatible triplets between m0, m1, and m2 = m1 - 2
      compatible_triplets += check_compatible_triplets(m0, m1, event.modules[m1.module_number - 2])
    else:
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

  for t in compatible_triplets:
    print_compatible_triplet_simplified(t, output_file)

hit_list_file = open(hit_list_filename, "w")
compatible_triplets_seeding_file = open(compatible_triplets_seeding_filename, "w")
compatible_triplets_forwarding_file = open(compatible_triplets_forwarding_filename, "w")

generate_hit_list(event, hit_list_file)
generate_compatible_triplets(event, compatible_triplets_seeding_file, seeding=True)
generate_compatible_triplets(event, compatible_triplets_forwarding_file, seeding=False, consider_missing_layers=True)

hit_list_file.close()
compatible_triplets_seeding_file.close()
compatible_triplets_forwarding_file.close()
