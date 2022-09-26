Started with the same configuration of the CNN as the lecture code for handwriting, with an adapted input/output and no dropout. Not successful as the accuracy was around 0.05
Doubling the convolutional and max-pooling layers helped masively, the accuracy on the training data was 0.96 and test data 0.93
Interesting effect - reducing the kernels to 2x2 reduced accuracy on training to 93, but improved it on test to 0.96. Means I was overfitting before?
Adding dropout (rate 0.3) to 3x3 scenario hidden layer: 0.95 training, 0.96 test
Adding same dropout to 2x2 scenario: 0.81 training, 0.89 test). Proceeding with 3x3 with dropout
Removing the second max-pooling layer helped the accuracy somewhat, 0.96 on training and 0.97 on test.
Changed max pooling to average pooling, no real effect.
Increasing the number of filters on conv layers to 64 did not help with the accuracy much, but made training the network slower, reverting.
Increasing the pooling size to 3x3 kept the accuracy and made the network faster to train, 4x4 started to reduce the accuracy.
Adding another hidden layer with 128 neurons reduced the accuracy, reverting. Splitting into two sequential 64 neuron layers was not successfull, reverting.
Sigmoid activation functions on the internal layers improved the accuracy to 0.98/0.98