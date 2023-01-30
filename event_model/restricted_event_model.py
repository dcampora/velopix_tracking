from copy import deepcopy
from event_model import event_model as em

class restricted_event_view:
  '''This is a view on the event that only exposes
  the hits and modules in the restricted layer list.'''
  def __init__(self, event, restricted_modules, restricted_mc):
    self.number_of_modules = len(restricted_modules)
    self.description = event.description + f" restricted to layers {restricted_modules}"
    self.montecarlo = restricted_mc
    self.module_zs = [a for i, a in enumerate(event.module_zs) if i in restricted_modules]

    # Recreate module_prefix_sum with only the considered modules
    self.module_prefix_sum = []
    ps = 0
    for m in restricted_modules:
      self.module_prefix_sum.append(ps)
      nb_of_hits = event.module_prefix_sum[m+1] - event.module_prefix_sum[m]
      ps += nb_of_hits
    self.module_prefix_sum.append(ps)
    self.number_of_hits = self.module_prefix_sum[-1]

    # Add hits
    self.hits = []
    for m in restricted_modules:
      hit_start = event.module_prefix_sum[m]
      nb_of_hits = event.module_prefix_sum[m+1] - hit_start
      for i in range(nb_of_hits):
        self.hits.append(event.hits[hit_start + i])

    # Add modules
    self.modules = [
      em.module(m,
        self.module_zs[m],
        self.module_prefix_sum[m],
        self.module_prefix_sum[m + 1] - self.module_prefix_sum[m],
        self.hits
      ) for m in range(0, self.number_of_modules)
    ]

def restrict_event(json_data, restricted_modules, restrict_min_nb_hits, restrict_consec_modules):
  # Restrict the data in the json according to the conditions imposed
  event = em.event(json_data)
  restricted_json = deepcopy(json_data)
  restricted_mc_particles = []
  for particle in restricted_json["montecarlo"]["particles"]:
    hits = particle[-1]
    accepted_hits = []
    # Remove all hits that do not belong to a hit in a valid module
    for hid in hits:
      hit = event.hits[hid]
      if hit.module_number in restricted_modules:
        accepted_hits.append(hid)
    
    # Require at least 3 hits
    if len(accepted_hits) < restrict_min_nb_hits:
      continue
    
    # Once we got the list of accepted hits, check if they are all in consecutive modules
    if restrict_consec_modules:
      current_module = event.hits[accepted_hits[0]].module_number
      for hid in accepted_hits[1:]:
        next_module = event.hits[hid].module_number
        if next_module != current_module + 2:
          continue
        current_module = next_module

    # Finally if all those conditions apply, add it to the list of new montecarlo particles
    mcp = particle
    mcp[-1] = accepted_hits
    restricted_mc_particles.append(mcp)

  restricted_json["montecarlo"]["particles"] = restricted_mc_particles
  restricted_event = restricted_event_view(event, restricted_modules, restricted_json["montecarlo"])

  # print("Restricted number of MC particles:", len(restricted_mc_particles))

  return restricted_event, restricted_json
