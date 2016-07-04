from classical_solver import classical_solver
import event_model as em
import validator_lite as vl
import json
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.3f')

def open_json_event(event_number, container_folder="velojson/"):
  f = open(container_folder + str(event_number) + ".json")
  json_data = json.loads(f.read())
  event = em.event(json_data)
  f.close()
  return json_data, event

def get_normalized_hits(hits, limits):
  n = lambda hit, limits, attribute: \
    (getattr(hit, attribute) + abs(limits[attribute][0])) / (abs(limits[attribute][0]) + abs(limits[attribute][1]))
 
  return [n(hits[0], limits, "x"), n(hits[0], limits, "y"), n(hits[0], limits, "z"), \
    n(hits[1], limits, "x"), n(hits[1], limits, "y"), n(hits[1], limits, "z"), \
    n(hits[2], limits, "x"), n(hits[2], limits, "y"), n(hits[2], limits, "z")]

def get_tracks_and_truth(event_number, hit_coord_limits, container_folder="velojson/"):
  try:
    json_data, event = open_json_event(event_number, container_folder)
    classical = classical_solver()
    classical_tracks = classical.solve(event)
    three_hit_tracks = [t for t in classical_tracks if len(t.hits) == 3]
    if len(three_hit_tracks) > 0:
      tracks_ghost_list = vl.identify_ghost_tracks(json_data, three_hit_tracks)
      track_input = [get_normalized_hits(t.hits, hit_coord_limits) for t in three_hit_tracks]
      truth = tracks_ghost_list
      return [track_input, truth]
    else:
      return [[], []]
  except e:
    print(e)
    return [[], []]

def main(number_of_events=100, container_folder="velojson/"):
  hit_coord_limits = {
    "x": (-49.702538, 49.741428),
    "y": (-50.506866, 50.526314),
    "z": (-288.031006, 750.531006)
  }

  # Let's use several processors to speed this up a little
  from multiprocessing import Pool
  pool = Pool()

  pool_results = [pool.apply_async(get_tracks_and_truth, (i, hit_coord_limits, container_folder)) \
    for i in range(number_of_events)]
  tracks_truth = [res.get(timeout=None) for res in pool_results]

  # Join in all results
  data = {"tracks": [], "truth": []}
  for temp_tracks, temp_truth in tracks_truth:
    data["tracks"] += temp_tracks
    data["truth"] += temp_truth

  # Print them to a file
  with open('tracks_truth_data.json', 'w') as outfile:
    json.dump(data, outfile)


def ghost_buster(json_file):
  f = open(json_file)
  json_data = json.loads(f.read())
  f.close()

  # 275271
  # print(len(json_data['tracks']))

  import tensorflow as tf
  import numpy as np

  # Training set
  # How about just the relative relation between hits?
  json_data["slopes"] = []
  for t in json_data["tracks"]:
    slopes = [(t[0] - t[3] + 1) / 2, (t[1] - t[4] + 1) / 2, (t[2] - t[5] + 1) / 2,
      (t[3] - t[6] + 1) / 2, (t[4] - t[7] + 1) / 2, (t[5] - t[8] + 1) / 2]
    json_data["slopes"].append(slopes)

  x = tf.placeholder(tf.float32, [None, 9])
  W = tf.Variable(tf.zeros([9, 1]))
  b = tf.Variable(tf.zeros([1]))

  y = tf.nn.softmax(tf.matmul(x, W) + b)
  y_ = tf.placeholder(tf.float32, [None, 1])
  
  # cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
  train_step = tf.train.GradientDescentOptimizer(0.5).minimize(y_ - y)
  
  init = tf.initialize_all_variables()
  sess = tf.Session()
  sess.run(init)

  # Train the system
  # for i in range(1000):
  #   batch_xs = np.array(json_data['tracks'][i*100:((i+1)*100)-1])
  #   batch_ys = np.array([[a] for a in json_data['truth'][i*100:((i+1)*100)-1]])
  #   sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})

  correct_prediction = tf.equal(y, y_)
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  print(correct_prediction, accuracy)

  print("Running predictions")
  for i in range(1000, 1010):
    batch_xs = np.array(json_data['tracks'][i*100:((i+1)*100)-1])
    batch_ys = np.array([[a] for a in json_data['truth'][i*100:((i+1)*100)-1]])
    print(sess.run(accuracy, feed_dict={x: batch_xs, y_: batch_ys}))


  # sigmoid = trans.LogSig()
  # gb_sizes = [6, 10, 10, 1]
  # gb = net.newff(minmax=[[0, 1] for _ in range(gb_sizes[0])], size=gb_sizes, transf=[sigmoid]*len(gb_sizes))
  
  # net_input = np.array(json_data["slopes"])
  # net_truth_input = np.array([[a] for a in json_data["truth"]])

  # # Train the network
  # sim0 = gb.sim(net_input)
  # error0 = gb.errorf(net_truth_input, sim0)
  # print("Starting error:", error0)
  # gb.train(net_input, net_truth_input, epochs=500, show=20, goal=0.001)
  # sim1 = gb.sim(net_input)
  # error1 = gb.errorf(net_truth_input, sim1)
  # print("Finishing error:", error1)
  
  # for i in range(len(sim1)):
  #   print(training_set["truth"][i], sim1[i])

  # ########################

  # import tensorflow as tf
  # import numpy as np

  # # Create 100 phony x, y data points in NumPy, y = x * 0.1 + 0.3
  # x_data = np.random.rand(100).astype(np.float32)
  # y_data = x_data * 0.1 + 0.3

  # # Try to find values for W and b that compute y_data = W * x_data + b
  # # (We know that W should be 0.1 and b 0.3, but Tensorflow will
  # # figure that out for us.)
  # W = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
  # b = tf.Variable(tf.zeros([1]))
  # y = W * x_data + b

  # # Minimize the mean squared errors.
  # loss = tf.reduce_mean(tf.square(y - y_data))
  # optimizer = tf.train.GradientDescentOptimizer(0.5)
  # train = optimizer.minimize(loss)

  # # Before starting, initialize the variables.  We will 'run' this first.
  # init = tf.initialize_all_variables()

  # # Launch the graph.
  # sess = tf.Session()
  # sess.run(init)

  # # Fit the line.
  # for step in range(201):
  #     sess.run(train)
  #     if step % 20 == 0:
  #         print(step, sess.run(W), sess.run(b))

  # # Learns best fit is W: [0.1], b: [0.3]



if __name__ == '__main__':
  ghost_buster("three_hit_tracks_truth_data.json")
  # main()
