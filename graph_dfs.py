from event_model import *

class segment(object):
  '''A segment for the graph dfs.'''
  def __init__(self, h0, h1, seg_number):
    self.h0 = h0
    self.h1 = h1
    self.weight = 0
    self.segment_number = seg_number
    self.root_segment = False

  def __repr__(self):
    return "Segment " + str(self.segment_number) + ":\n" + \
      " h0: " + str(self.h0) + "\n" + \
      " h1: " + str(self.h1) + "\n" + \
      " Weight: " + str(self.weight)


class graph_dfs(object):
  '''This method creates a directed graph, and traverses
  it with a DFS method in order to create tracks.

  It grabs inspiration from the "CA" algorithm.

  Steps:
  0. Preorder all hits in each sensor by x,
     and update their hit_number.

  1. Fill candidates
      index: hit index
      contents: [candidate start, candidate end]
  
  2. Create all segments, indexed by outer hit number.

  3. Assign weights and get roots.

  4. Depth first search.
  '''

  def __init__(self, max_slopes=(0.7, 0.7), max_tolerance=(0.4, 0.4), max_scatter=0.4, \
    minimum_root_weight=1, weight_assignment_iterations=2, allowed_missing_sensor_hits=2, \
    allow_cross_track=True):
    self.__max_slopes = max_slopes
    self.__max_tolerance = max_tolerance
    self.__max_scatter = max_scatter
    self.__minimum_root_weight = minimum_root_weight
    self.__weight_assignment_iterations = weight_assignment_iterations
    self.__allow_cross_track = allow_cross_track
    self.__allowed_missing_sensor_hits = allowed_missing_sensor_hits

  def are_compatible_in_x(self, hit_0, hit_1):
    '''Checks if two hits are compatible according
    to the configured max_slope in x.
    '''
    hit_distance = abs(hit_1[2] - hit_0[2])
    dxmax = self.__max_slopes[0] * hit_distance
    return abs(hit_1[0] - hit_0[0]) < dxmax

  def are_compatible_in_y(self, hit_0, hit_1):
    '''Checks if two hits are compatible according
    to the configured max_slope in y.
    '''
    hit_distance = abs(hit_1[2] - hit_0[2])
    dymax = self.__max_slopes[1] * hit_distance
    return abs(hit_1[1] - hit_0[1]) < dymax

  def are_compatible(self, hit_0, hit_1):
    '''Checks if two hits are compatible according to
    the configured max_slope.
    '''
    return self.are_compatible_in_x(hit_0, hit_1) and \
      self.are_compatible_in_y(hit_0, hit_1)

  def check_tolerance(self, hit_0, hit_1, hit_2):
    '''Checks if three hits are compatible by
    extrapolating the segment conformed by the
    first two hits (hit_0, hit_1) and comparing
    it to the third hit.

    The parameters that control this tolerance are
    max_tolerance and max_scatter.
    '''
    td = 1.0 / (hit_1.z - hit_0.z)
    txn = hit_1.x - hit_0.x
    tyn = hit_1.y - hit_0.y
    tx = txn * td
    ty = tyn * td

    dz = hit_2.z - hit_0.z
    x_prediction = hit_0.x + tx * dz
    dx = abs(x_prediction - hit_2.x)
    tolx_condition = dx < self.__max_tolerance[0]

    y_prediction = hit_0.y + ty * dz
    dy = abs(y_prediction - hit_2.y)
    toly_condition = dy < self.__max_tolerance[1]

    scatterNum = (dx * dx) + (dy * dy)
    scatterDenom = 1.0 / (hit_2.z - hit_1.z)
    scatter = scatterNum * scatterDenom * scatterDenom

    scatter_condition = scatter < self.__max_scatter
    return tolx_condition and toly_condition and scatter_condition

  def are_segments_compatible(self, seg0, seg1):
    '''Checks whether two segments are compatible, applying
    the tolerance check.

    seg1 should start where seg0 ends
    (ie. seg0.h1 and seg1.h0 should be the same).
    '''
    if seg0.h1 != seg1.h0:
      print("Warning: seg0 h1 and seg1 h0 are not the same")
      print(seg0.h1)
      print(seg1.h0)
    return self.check_tolerance(seg0.h0, seg0.h1, seg1.h1)

  def order_hits(self, event):
    '''Preorder all hits in each sensor by x,
    and update their hit_number.
    '''
    for hit_start, hit_end in [(s.hit_start_index, s.hit_end_index) for s in event.sensors]:
      event.hits[hit_start:hit_end] = sorted(event.hits[hit_start:hit_end], key=lambda h: h.x)
    for h in range(0, len(event.hits)):
      event.hits[h].hit_number = h

  def fill_candidates(self, event):
    '''Fill candidates
    index: hit index
    contents: {sensor_index: [candidate start, candidate end], ...}
    '''
    candidates = [{} for i in range(0, event.number_of_hits)]
    for s0, starting_sensor_index in zip(reversed(event.sensors[2:]), reversed(range(0, len(event.sensors) - 2))):
      for h0 in s0.hits():
        for missing_sensors in range(0, self.__allowed_missing_sensor_hits + 1):
          sensor_index = starting_sensor_index - missing_sensors * 2
          if self.__allow_cross_track:
            sensor_index = starting_sensor_index - missing_sensors
          if sensor_index >= 0:
            s1 = event.sensors[sensor_index]
            begin_found = False
            end_found = False
            candidates[h0.hit_number][sensor_index] = [-1, -1]
            for h1 in s1.hits():
              if not begin_found and self.are_compatible_in_x(h0, h1):
                candidates[h0.hit_number][sensor_index][0] = h1.hit_number
                candidates[h0.hit_number][sensor_index][1] = h1.hit_number + 1
                begin_found = True
              elif begin_found and not self.are_compatible_in_x(h0, h1):
                candidates[h0.hit_number][sensor_index][1] = h1.hit_number
                end_found = True
                break
            if begin_found and not end_found:
              candidates[h0.hit_number][sensor_index][1] = s1.hits()[-1].hit_number+1
    return candidates

  def populate_segments(self, event, candidates):
    '''Create segments and populate compatible segments.

    segments: All segments.
    
    outer_hit_segment_list: Segment indices, indexed by outer hit.
                            Note: Outer hit number is the one with smaller z.

    compatible_segments: Compatible segment indices, indexed by segment index.

    populated_compatible_segments: Indices of all compatible_segments.
    '''
    segments = []
    outer_hit_segment_list = [[] for _ in event.hits]
    for h0_number in range(0, event.number_of_hits):
      for sensor_number, sensor_candidates in iter(candidates[h0_number].items()):
        for h1_number in range(sensor_candidates[0], sensor_candidates[1]):
          if self.are_compatible_in_y(event.hits[h0_number], event.hits[h1_number]):
            segments.append(segment(event.hits[h0_number], event.hits[h1_number], len(segments)))
            outer_hit_segment_list[h1_number].append(len(segments) - 1)

    compatible_segments = [[] for _ in segments]
    for seg1 in segments:
      for seg0_index in outer_hit_segment_list[seg1.h0.hit_number]:
        seg0 = segments[seg0_index]
        if self.are_segments_compatible(seg0, seg1):
          compatible_segments[seg0.segment_number].append(seg1.segment_number)

    populated_compatible_segments = [seg_index for seg_index in range(0, len(compatible_segments)) \
      if len(compatible_segments[seg_index]) > 0]

    return (segments, outer_hit_segment_list, compatible_segments, populated_compatible_segments)

  def assign_weights_and_populate_roots(self, segments, compatible_segments, populated_compatible_segments):
    '''Assigns weights to the segments according to the configured
    number of iterations weight_assignment_iterations.

    It also populates the root_segment attribute of segments.
    '''
    for _ in range(0, self.__weight_assignment_iterations):
      for seg0_index in populated_compatible_segments:
        segments[seg0_index].weight = max([segments[seg_number].weight for seg_number in compatible_segments[seg0_index]]) + 1

    # Find out root segments
    # Mark all as root
    for seg0_index in populated_compatible_segments:
      segments[seg0_index].root_segment = True

    # Traverse the populated_compatible_segments and turn the
    # found ones to False
    for seg0_index in populated_compatible_segments:
      for seg1_index in compatible_segments[seg0_index]:
        segments[seg1_index].root_segment = False

  def dfs(self, segment, segments, compatible_segments):
    '''Returns tracks found extrapolating this segment,
    by traversing the segments following a depth first search strategy.
    '''
    if len(compatible_segments[segment.segment_number]) == 0:
      return [[segment.h1]]
    else:
      for segid in compatible_segments[segment.segment_number]:
        return [[segment.h1] + dfs_segments for dfs_segments in self.dfs(segments[segid], segments, compatible_segments)]

  def print_compatible_segments(self, segments, compatible_segments, populated_compatible_segments):
    '''Prints all compatible segments.'''
    for seg0_index in populated_compatible_segments:
      seg0 = segments[seg0_index]
      print("%s\nis compatible with segments \n%s\n" % (seg0, [segments[seg_index] for seg_index in compatible_segments[seg0_index]]))
      
  def solve(self, event):
    '''Solves the event according to the strategy
    defined in the class definition.
    '''
    print("Invoking graph dfs with\n max slopes: %s\n max tolerance: %s\n\
 max scatter: %s\n weight assignment iterations: %s\n minimum root weight: %s\n\
 allowed missing sensor hits: %s\n allow cross track: %s (will only take effect if allowed missing sensor hits > 0)\n\n" % \
 (self.__max_slopes, self.__max_tolerance, self.__max_scatter, self.__weight_assignment_iterations, \
  self.__minimum_root_weight, self.__allowed_missing_sensor_hits, self.__allow_cross_track))

    # 0. Preorder all hits in each sensor by x,
    #    and update their hit_number.
    
    # Work with a copy of event
    event_copy = event.copy()
    self.order_hits(event_copy)

    # 1. Fill candidates
    #     index: hit index
    #     contents: [candidate start, candidate end]
    candidates = self.fill_candidates(event_copy)
  
    # 2. Create all segments, indexed by outer hit number
    (segments, outer_hit_segment_list, compatible_segments, populated_compatible_segments) = \
      self.populate_segments(event_copy, candidates)

    # self.print_compatible_segments(segments, compatible_segments, populated_compatible_segments)

    # 3. Assign weights and get roots
    self.assign_weights_and_populate_roots(segments, compatible_segments, populated_compatible_segments)

    root_segments = [segid for segid in populated_compatible_segments \
      if segments[segid].root_segment == True and \
         segments[segid].weight >= self.__minimum_root_weight]
    
    # print("Found %d root segments" % (len(root_segments)))
    
    # 4. Depth first search
    tracks = []
    for segment_id in root_segments:
      root_segment = segments[segment_id]
      tracks += [track([root_segment.h0] + dfs_segments) for dfs_segments in self.dfs(root_segment, segments, compatible_segments)]

    return tracks
