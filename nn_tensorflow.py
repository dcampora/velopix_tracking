import tensorflow as tf
from tensorflow.python.ops.math_ops import sigmoid
from tensorflow.python.ops.rnn_cell import _linear as linear
from tensorflow.python.ops import variable_scope as vs

class linearizer(object):
  def __init__(self):
    self.i = 0

  def get(self, c, n):
    self.i += 1
    with vs.variable_scope(str(self.i)):
      return linear([c], n, True)


class classical_trainer(object):
  def __init__(self, layers, training_parameters, linearizer=linearizer()):
    self.layers_specification = layers
    self.training_parameters = training_parameters
    self.linearizer = linearizer
    self.generate()

  def generate(self):
    self.x = tf.placeholder(tf.float32, [None, self.layers_specification[0]])
    self.y_ = tf.placeholder(tf.float32, [None, self.layers_specification[-1]])
    
    # hidden layers
    self.hidden_layers = [self.x]
    for l in self.layers_specification[1:]:
      self.hidden_layers.append(self.linearizer.get(self.hidden_layers[-1], l))

    # ending in a sigmoid
    self.y = sigmoid(self.hidden_layers[-1])

    # training step is determined to minimize the cross entropy
    # with some method
    self.cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(self.y, self.y_)
    self.train_step = tf.train.GradientDescentOptimizer(self.training_parameters["rate"]).minimize(self.cross_entropy)

    # start the session
    self.init = tf.initialize_all_variables()
    self.sess = tf.Session()
    self.sess.run(self.init)

  def train(self, training_set_x, training_set_y, batch_size=100):
    # print("Training ...")
    for i in range(int(len(training_set_x) / batch_size)):
      batch_xs = np.array(training_set_x[i*batch_size:(i+1)*batch_size])
      batch_ys = np.array(training_set_y[i*batch_size:(i+1)*batch_size])
      self.sess.run(self.train_step, feed_dict={self.x: batch_xs, self.y_: batch_ys})

  def validate(self, validation_set_x, validation_set_y,):
    # print("Validating predictions ...")
    correct_prediction = tf.equal(self.y, self.y_)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    batch_xs = np.array(validation_set_x)
    batch_ys = np.array(validation_set_y)
    return self.sess.run(accuracy, feed_dict={self.x: batch_xs, self.y_: batch_ys})
