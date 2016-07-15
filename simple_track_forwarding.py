import tempfile
import json
import event_model as em
import validator_lite as vl
import numpy as np
import tensorflow as tf
from nn_tensorflow import classical_trainer

def open_json_event(event_number, container_folder="velojson/"):
  f = open(container_folder + str(event_number) + ".json")
  json_data = json.loads(f.read())
  event = em.event(json_data)
  f.close()
  return json_data, event

def ghost_buster(json_file):
  f = open(json_file)
  json_data = json.loads(f.read())
  f.close()

  # print(len(json_data['tracks']))
  # 275271

  ## ###########################
  ##
  ## Training with DNNClassifier
  ##
  ## ###########################

  # # Convert into tensorflow format (AOS to SOA)
  number_train_values = 200000
  number_eval_values  = 1000

  # Respect the ratio
  training_set = {"x": [], "y": []}
  number_of_examples = len([a for a in json_data['truth'][:number_train_values] if a == 0]), \
    len([a for a in json_data['truth'][:number_train_values] if a == 1])
  min_no_ex = min(number_of_examples[0], number_of_examples[1])
  good_examples, bad_examples = 0, 0
  for i in range(number_train_values):
    if json_data['truth'][i] == 0 and bad_examples < min_no_ex:
      bad_examples += 1
    elif json_data['truth'][i] == 1 and good_examples < min_no_ex:
      good_examples += 1
    else:
      continue
    training_set["x"].append(json_data['tracks'][i])
    training_set["y"].append(json_data['truth'][i])
  # print("Number of examples in training set:", len(training_set["x"]))

  training_set = {"x": np.array(training_set["x"]),
    "y": np.array(training_set["y"])}
  validation_set = {"x": np.array(json_data['tracks'][number_train_values:number_train_values+number_eval_values]),
    "y": np.array(json_data['truth'][number_train_values:number_train_values+number_eval_values])}

  model_dir = tempfile.mkdtemp()
  layers = [100, 100, 100]
  classifier = tf.contrib.learn.DNNClassifier(model_dir=model_dir, hidden_units=layers)
  # h_fc1 = tf.contrib.learn.ops.dnn(h_pool2_flat, [1024], activation=tf.nn.relu, dropout=0.5)
  
  classifier.fit(x=training_set["x"], y=training_set["y"], steps=200)
  results = classifier.evaluate(x=validation_set["x"], y=validation_set["y"], steps=1)
  
  for key in sorted(results):
    print("%s: %s" % (key, results[key]))

  # Classify a new sample
  import random
  new_samples = []
  for i in range(100):
    new_samples.append([random.randint(0, 100) / 100 for _ in range(9)])

  new_samples = np.array(new_samples, dtype=float)
  y = classifier.predict(new_samples)

  print ('Predictions: {}'.format(str(y)))

  ## ######################################
  ##
  ## Training with cooked up Neural Network 
  ##
  ## ######################################
  
  # Training set
  # How about just the relative relation between hits?
  # json_data["slopes"] = []
  # for t in json_data["tracks"]:
  #   slopes = [t[0], t[1], t[2],
  #     (t[0] - t[3] + 1) / 2, (t[1] - t[4] + 1) / 2, (t[2] - t[5] + 1) / 2,
  #     (t[3] - t[6] + 1) / 2, (t[4] - t[7] + 1) / 2, (t[5] - t[8] + 1) / 2]
  #   json_data["slopes"].append(slopes)
  
  # number_train_values = 200000
  # # ratio_train_good_examples = 0.5
  # number_eval_values  = 1000
  # layers = [9, 100, 100, 100, 1]
  # training_rate = 0.9

  # json_data_truth = [[a] for a in json_data['truth']]

  # # Respect the ratio
  # training_set = {"x": [], "y": []}
  # number_of_examples = len([a[0] for a in json_data_truth[:number_train_values] if a[0] == 0]), \
  #   len([a[0] for a in json_data_truth[:number_train_values] if a[0] == 1])
  # min_no_ex = min(number_of_examples[0], number_of_examples[1])
  # good_examples, bad_examples = 0, 0
  # for i in range(number_train_values):
  #   if json_data_truth[i][0] == 0 and bad_examples < min_no_ex:
  #     bad_examples += 1
  #   elif json_data_truth[i][0] == 1 and good_examples < min_no_ex:
  #     good_examples += 1
  #   else:
  #     continue
  #   training_set["x"].append(json_data['tracks'][i])
  #   training_set["y"].append(json_data_truth[i])
  # # print("Number of examples in training set:", len(training_set["x"]))

  # # training_set = {"x": json_data['tracks'][:number_train_values],
  # #   "y": json_data_truth[:number_train_values]}
  # validation_set = {"x": json_data['tracks'][number_train_values:number_train_values+number_eval_values],
  #   "y": json_data_truth[number_train_values:number_train_values+number_eval_values]}

  # print("layers, neurons, rate, accuracy")
  # for num_hidden_layers in [1, 2, 3, 5, 10]:
  #   for size_hidden_layers in [10, 20, 50, 100]:
  #     layers = [9] + [size_hidden_layers for _ in range(num_hidden_layers)] + [1]

  #     results = {'rate': [], 'accuracy': []}
  #     for i in range(50, 80, 5):
  #       training_rate = i / 100

  #       ct = classical_trainer(layers, {"rate": training_rate})
  #       ct.train(training_set["x"], training_set["y"])
  #       results['rate'].append(training_rate)
  #       results['accuracy'].append(ct.validate(validation_set["x"], validation_set["y"]))

  #     max_rate = max(results['accuracy'])
  #     for i in range(len(results['rate'])):
  #       if results['accuracy'][i] == max_rate:
  #         print(num_hidden_layers, ",", size_hidden_layers, ",", results['rate'][i], ",", results['accuracy'][i])
  #         break


  ## ################################################
  ##
  ## Training with cooked up Neural Network (sklearn)
  ##
  ## ################################################

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


def main(_):
  ghost_buster("three_hit_tracks_truth_data.json")

if __name__ == "__main__":
  tf.app.run()
