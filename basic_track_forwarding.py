import classical_solver as cs
import event_model as em
import validator_lite as vl

# Get an event
import json
f = open("velojson/20.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Get all tracks by using the classical method and print them
print("Invoking classical solver...")
classical = cs.classical_solver()
classical_tracks = classical.solve(event)
print("Found", len(classical_tracks), "tracks")

vl.validate_print([json_data], [classical_tracks])
print(vl.validate_efficiency([json_data], [classical_tracks]))
print(vl.validate_clone_fraction([json_data], [classical_tracks]))
print(vl.validate_ghost_fraction([json_data], [classical_tracks]))
