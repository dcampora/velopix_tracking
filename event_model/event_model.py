import hashlib

class event(object):
  '''Event defined by its json description.'''
  def __init__(self, json_data):
    self.number_of_modules = 52
    self.description = json_data["description"]
    self.montecarlo = json_data["montecarlo"]
    self.module_prefix_sum = json_data["module_prefix_sum"]
    self.number_of_hits = self.module_prefix_sum[self.number_of_modules]
    self.module_zs = []
    self.hits = []
    with_t = "t" in json_data

    for m in range(self.number_of_modules):
      self.module_zs.append(set([]))
      for i in range(self.module_prefix_sum[m], self.module_prefix_sum[m + 1]):
        if with_t:
          self.hits.append(hit(json_data["x"][i], json_data["y"][i], json_data["z"][i], i, m, json_data["t"][i], 1))
        else:
          self.hits.append(hit(json_data["x"][i], json_data["y"][i], json_data["z"][i], i, m))
        self.module_zs[m].add(json_data["z"][i])
    
    self.modules = [
      module(m,
        self.module_zs[m],
        self.module_prefix_sum[m],
        self.module_prefix_sum[m + 1] - self.module_prefix_sum[m],
        self.hits
      ) for m in range(0, self.number_of_modules)
    ]

class track(object):
  '''A track, essentially a list of hits.'''
  def __init__(self, hits):
    self.hits = hits
    self.missed_last_module = False
    self.missed_penultimate_module = False

  def add_hit(self, hit):
    self.hits.append(hit)

  def __repr__(self):
    return "Track with " + str(len(self.hits)) + " hits: " + str(self.hits)

  def __iter__(self):
    return iter(self.hits)

  def __eq__(self, other):
    return self.hits == other.hits

  def __ne__(self, other):
    return not self.__eq__(other)

  def __hash__(self):
      return int.from_bytes(hashlib.sha256(
        ''.join([str(h.id) for h in self.hits]).encode('utf-8')).digest(), byteorder='big')


class hit(object):
  '''A hit, composed of an id and its x, y and z coordinates.
  It may optionally contain the number of the module where
  the hit happened.
  '''
  def __init__(self, x, y, z, hit_id, module=-1, t=0, with_t=False):
    self.x = x
    self.y = y
    self.z = z
    self.t = t
    self.id = hit_id
    self.module_number = module
    self.with_t = with_t

  def __getitem__(self, index):
    if (index<0 or index>2):
      raise IndexError

    if (index==0): return self.x
    elif(index==1): return self.y
    else: return self.z

  def __repr__(self):
    return "#" + str(self.id) + " module " + str(self.module_number) + " {" + str(self.x) + ", " + \
         str(self.y) + ", " + str(self.z) + (", " + str(self.t) if self.with_t else "") + "}"

  def __eq__(self, other):
      return self.id == other.id

  def __ne__(self, other):
      return not self.__eq__(other)

  def __hash__(self):
      return self.id


class module(object):
  '''A module is identified by its number.
  It also contains the z coordinate in which it sits, and
  the list of hits it holds.

  Note modules are ordered by z, so the less the module_number,
  the less the z.
  '''
  def __init__(self, module_number, z, start_hit, number_of_hits, hits):
    self.module_number = int(module_number)
    self.z = z
    self.hit_start_index = start_hit
    self.hit_end_index = start_hit + number_of_hits
    self.__global_hits = hits

  def __iter__(self):
    return iter(self.__global_hits[self.hit_start_index : self.hit_end_index])

  def __repr__(self):
    return "module " + str(self.module_number) + ":\n" + \
      " At z: " + str(self.z) + "\n" + \
      " Number of hits: " + str(len(self.hits())) + "\n" + \
      " Hits (#id {x, y, z}): " + str(self.hits())

  def hits(self):
    return self.__global_hits[self.hit_start_index : self.hit_end_index]
