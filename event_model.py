from sklearn import linear_model
from hashlib import sha256
from math import floor

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


class track(object):
  '''A track, essentially a list of hits.'''
  def __init__(self, hits):
    self.hits = hits

  def add_hit(self, hit):
    self.hits.append(hit)

  # def chi2(self):
  #   # Get a linear regression
  #   xy = [[h.x, h.y] for h in self.hits]
  #   z  = [h.z for h in self.hits]
  #   lr = linear_model.LinearRegression()
  #   lr.fit(xy, z)
  #   # Calculate chi square
  #   # chi2 = sum((o_i - e_i)^2 / e_i)
  #   observed = lr.predict(xy)
  #   return sum([((o-e)*(o-e))/e for o, e in zip(observed, z)])
  
  # def chi2(self):
  #   # Get two linear regressions in 2D
  #   xs = [[h.x] for h in self.hits]
  #   ys = [[h.y] for h in self.hits]
  #   zs = [h.z for h in self.hits]
  #   lx = linear_model.LinearRegression()
  #   lx.fit(xs, zs)
  #   ly = linear_model.LinearRegression()
  #   ly.fit(ys, zs)
  #   # Calculate chi square
  #   # chi2 = sum((o_i - e_i)^2 / e_i)
  #   obs_x = lx.predict(xs)
  #   obs_y = ly.predict(ys)
  #   return sum([(ox-ex)*(ox-ex) + (oy-ey)*(oy-ey) for ox, oy, ex, ey in zip(obs_x, obs_y, xs, ys)])

  def chi2(self):
    # Get chi2 of track
    # Code extracted from LHCb reconstruction
    # Obtain x0, y0, tx, ty parameters
    w = 3966.94
    s0, sx, sz, sxz, sz2 = 0, 0, 0, 0, 0
    u0, uy, uz, uyz, uz2 = 0, 0, 0, 0, 0
    for hit in self.hits:
      x, y, z = hit.x, hit.y, hit.z
      wx = w * x
      wz = w * z
      s0 += w
      sx += wx
      sz += wz
      sxz += wx * z
      sz2 += wz * z
      wy = w * y
      u0 += w
      uy += wy
      uz += wz
      uyz += wy * z
      uz2 += wz * z
    dens = 1.0 / (sz2 * s0 - sz * sz)
    if abs(dens) > 10e+10:
      dens = 1.0
    tx = (sxz * s0 - sx * sz) * dens
    x0 = (sx * sz2 - sxz * sz) * dens
    denu = 1.0 / (uz2 * u0 - uz * uz)
    if abs(denu) > 10e+10:
      denu = 1.0
    ty = (uyz * u0 - uy * uz) * denu
    y0 = (uy * uz2 - uyz * uz) * denu

    # Get chi2
    ndof = -4
    chi2 = []
    for hit in self.hits:
      x = x0 + tx * hit.z
      y = y0 + ty * hit.z
      dx = x - hit.x
      dy = y - hit.y
      chi2.append(dx * dx * w + dy * dy * w)
      ndof += 2
    # return chi2
    return sum(chi2) / ndof

  def interleaved_sensors_relative(self):
    int_sensors = 0
    prev_sensor_number = -1
    number_of_sensors = len(self.hits)
    for h in sorted(self.hits):
      if prev_sensor_number == -1:
        prev_sensor_number = h.sensor_number
      else:
        sensor_number_difference = abs(h.sensor_number - prev_sensor_number)
        if sensor_number_difference >= 3:
          int_sensors += floor((sensor_number_difference - 1) / 2)
        prev_sensor_number = h.sensor_number
    return int_sensors / number_of_sensors

  def length(self):
    return len(self.hits)

  def __repr__(self):
    return "Track hits #" + str(len(self.hits)) + ": " + str(self.hits)

  def __iter__(self):
    return iter(self.hits)

  def __eq__(self, other):
    return self.hits == other.hits

  def __ne__(self, other):
    return not self.__eq__(other)

  def __hash__(self):
    return int.from_bytes(sha256(
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
    if (index<0 or index>2):
      raise IndexError

    if (index==0): return self.x
    elif(index==1): return self.y
    else: return self.z

  def __repr__(self):
    return "#" + str(self.id) + " {" + str(self.x) + ", " + \
           str(self.y) + ", " + str(self.z) + "}"

  def __eq__(self, other):
    return self.id == other.id

  def __ne__(self, other):
    return not self.__eq__(other)

  def __hash__(self):
    return self.id

  def __lt__(self, other):
    return self.id < other.id


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

