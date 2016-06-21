import hashlib

class segment(object):
  '''Segment extrapolated.'''
  def __init__(self, hits, function):
    self.hits = hits
    self.x, self.y, self.z, self.slope = function(hits)

  def __getitem__(self, index):
    if (index==0): return self.x
    elif (index==1): return self.y
    else: raise IndexError

  def __eq__(self, other):
    return self.hits == other.hits

  def __ne__(self, other):
    return not self.__eq__(other)


class event(object):
  '''Event defined by its json description.'''
  def __init__(self, json_description):
    self.event = json_description["event"]
    self.montecarlo = json_description["montecarlo"]
    self.number_of_sensors = self.event["number_of_sensors"]
    self.number_of_hits = self.event["number_of_hits"]
    self.hits = []
    for s in range(self.number_of_sensors):
      for i in range(self.event["sensor_hits_starting_index"][s], 
      self.event["sensor_hits_starting_index"][s] + self.event["sensor_number_of_hits"][s]):
        self.hits.append(hit(self.event["hit_x"][i], self.event["hit_y"][i], self.event["hit_z"][i],
        self.event["hit_id"][i], s))
    self.sensors = [sensor(s, self.event["sensor_module_z"][s],
      self.hits[self.event["sensor_hits_starting_index"][s] : 
      self.event["sensor_hits_starting_index"][s] + self.event["sensor_number_of_hits"][s]])
      for s in range(0, self.number_of_sensors)]
    self.hit_dictionary = {h.id:h for h in self.hits}


class track(object):
  '''A track, essentially a list of hits.'''
  def __init__(self, hits):
    self.hits = hits

  def add_hit(self, hit):
    self.hits.append(hit)

  def __repr__(self):
    return "Track hits #" + str(len(self.hits)) + ": " + str(self.hits)

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
  It may optionally contain the number of the sensor where
  the hit happened.
  '''
  def __init__(self, x, y, z, hit_id, sensor=-1):
    self.x = x
    self.y = y
    self.z = z
    self.id = hit_id
    self.sensor_number = sensor

  def __getitem__(self, index):
    if (index==0): return self.x
    elif(index==1): return self.y
    elif(index==2): return self.z
    else: raise IndexError

  def __repr__(self):
    return "#" + str(self.id) + " {" + str(self.x) + ", " + \
           str(self.y) + ", " + str(self.z) + "}"

  def __eq__(self, other):
      return self.id == other.id

  def __ne__(self, other):
      return not self.__eq__(other)

  def __hash__(self):
      return self.id


class sensor(object):
  '''A sensor is identified by its number.
  It also contains the z coordinate in which it sits, and
  the list of hits it holds.

  Note sensors are ordered by z, so the less the sensor_number,
  the less the z.
  '''
  def __init__(self, sensor_number, z, hits):
    self.sensor_number = sensor_number
    self.hits = hits
    self.z = z

  def __iter__(self):
    return iter(self.hits)

  def __repr__(self):
    return "Sensor " + str(self.sensor_number) + ":\n" + \
      " At z: " + str(self.z) + "\n" + \
      " Number of hits: " + str(len(self.hits)) + "\n" + \
      " Hits (#id {x, y, z}): " + str(self.hits)

