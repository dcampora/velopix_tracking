class Sensor(object):
  def __init__(self, sensor_number, json_event):
    self.json_event = json_event
    self.sensor_number = sensor_number
    self.hits = HitsIterator(self.sensor_number, self.json_event)

  def __iter__(self):
    return HitsIterator(self.sensor_number, self.json_event)

  def __repr__(self):
    return "Sensor " + str(self.sensor_number) + ":\n" + \
      " At z: " + str(self.get_z()) + "\n" + \
      " Number of hits: " + str(self.get_number_of_hits()) + "\n" + \
      " Hits (x, y, z, ID): " + str(self.hits)
      
  def get_z(self):
    return self.json_event["sensor_module_z"][self.sensor_number]

  def get_number_of_hits(self):
    return self.json_event["sensor_number_of_hits"][self.sensor_number]    


class Hit(object):
  def __init__(self, x, y, z, hid):
    self.x = x
    self.y = y
    self.z = z
    self.id = hid

  def __getitem__(self, index):
    if (index<0 or index>3):
      raise IndexError

    if (index==0): return self.x
    elif(index==1): return self.y
    elif(index==2): return self.z
    else: return self.id

  def __repr__(self):
    return "#" + str(self.id) + " (" + str(self.x) + ", " + \
           str(self.y) + ", " + str(self.z) + ")"


class HitsIterator(object):
  def __init__(self, sensor_number, json_event):
    self.sensor_number = sensor_number
    self.starting_index = json_event["sensor_hits_starting_index"][sensor_number]
    self.number_of_hits = json_event["sensor_number_of_hits"][sensor_number]
    self.hit_X = json_event["hit_X"]
    self.hit_Y = json_event["hit_Y"]
    self.hit_Z = json_event["hit_Z"]
    self.hit_ID = json_event["hit_ID"]
    self.index = self.starting_index - 1
    self.last_index = self.starting_index + self.number_of_hits

  def __getitem__(self, i):
    index = self.starting_index + i
    if index < 0 or index >= self.last_index:
      raise IndexError
    return Hit(self.hit_X[index], self.hit_Y[index], self.hit_Z[index], self.hit_ID[index])

  def __next__(self):
    self.index += 1
    if self.index >= self.last_index:
      raise StopIteration
    return Hit(self.hit_X[self.index], self.hit_Y[self.index], self.hit_Z[self.index], self.hit_ID[self.index])

  def __str__(self):
    return str([h for h in self])
    
####

class Track(object):
  def __init__(self, hits):
    self.hits = hits

  def __repr__(self):
    return "Track hits #" + str(len(self.hits)) + ": " + str(self.hits) + "\n"

def are_compatible(hit_0, hit_1, max_slopes=(0.7, 0.7)):
  hit_distance = abs(hit_1[2] - hit_0[2])
  dxmax = max_slopes[0] * hit_distance
  dymax = max_slopes[1] * hit_distance
  return abs(hit_1[0] - hit_0[0]) < dxmax and \
         abs(hit_1[1] - hit_0[1]) < dymax

####

# Get an event
import json
f = open("velojson/0.json")
event_json = json.loads(f.read())
f.close()

# Get all sensors, print some information
sensors = [Sensor(i, event_json) for i in range(0, 52)]
print(sensors[0], "\n\n", sensors[1], "\n\n", sensors[2])

# We are searching for tracks
# We will keep a list of used hits to avoid clones
tracks    = []
used_hits = []

## Start from the last sensor, create seeds and forward them
# for s0, s1, starting_sensor_index in zip(reversed(sensors[3:]), reversed(sensors[1:-2]), reversed(range(0, 49))):
for s0, s1, starting_sensor_index in zip(reversed(sensors[3:5]), reversed(sensors[1:3]), reversed(range(0, 2))):
  for h0 in [h0 for h0 in s0 if h0[3] not in used_hits]:
    for h1 in [h1 for h1 in s1 if h1[3] not in used_hits]:
      
      if are_compatible(h0, h1):
        # We have a seed, let's attempt to form a track
        # with a hit from the following three sensors
        h2_found = False
        for sensor_index in [sid for sid in reversed(range(starting_sensor_index-2, starting_sensor_index+1)) if sid >= 0]:
          for h2 in sensors[sensor_index]:
            # if under_tolerance(h0, h1, h2):
            tracks.append( Track([h0, h1, h2]) )
            used_hits += [h0[3], h1[3], h2[3]]
            h2_found = True
            print (len(used_hits))
            break
          if h2_found:
            break
        if h2_found:
          break


        
print(tracks)

# C function for checking the hittotrack tolerance
#
# const float td = 1.0f / (h1_z - h0.z);
# const float txn = (h1_x - h0.x);
# const float tyn = (h1_y - h0.y);
# tx = txn * td;
# ty = tyn * td;
#       float fitHitToTrack(const float tx, const float ty, const struct CL_Hit* h0, const float h1_z, const struct CL_Hit* h2) {
#   // tolerances
#   const float dz = h2->z - h0->z;
#   const float x_prediction = h0->x + tx * dz;
#   const float dx = fabs(x_prediction - h2->x);
#   const bool tolx_condition = dx < PARAM_TOLERANCE;

#   const float y_prediction = h0->y + ty * dz;
#   const float dy = fabs(y_prediction - h2->y);
#   const bool toly_condition = dy < PARAM_TOLERANCE;

#   // Scatter - Updated to last PrPixel
#   const float scatterNum = (dx * dx) + (dy * dy);
#   const float scatterDenom = 1.f / (h2->z - h1_z);
#   const float scatter = scatterNum * scatterDenom * scatterDenom;

#   const bool scatter_condition = scatter < MAX_SCATTER;
#   const bool condition = tolx_condition && toly_condition && scatter_condition;

#   return condition * scatter + !condition * MAX_FLOAT;
# }