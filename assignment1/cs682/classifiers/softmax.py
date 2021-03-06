import numpy as np
import math
from random import shuffle

def softmax_loss_naive(W, X, y, reg):
  """
  Softmax loss function, naive implementation (with loops)

  Inputs have dimension D, there are C classes, and we operate on minibatches
  of N examples.

  Inputs:
  - W: A numpy array of shape (D, C) containing weights.
  - X: A numpy array of shape (N, D) containing a minibatch of data.
  - y: A numpy array of shape (N,) containing training labels; y[i] = c means
    that X[i] has label c, where 0 <= c < C.
  - reg: (float) regularization strength

  Returns a tuple of:
  - loss as single float
  - gradient with respect to weights W; an array of same shape as W
  """
  # Initialize the loss and gradient to zero.
  loss = 0.0
  dW = np.zeros_like(W)

  #############################################################################
  # TODO: Compute the softmax loss and its gradient using explicit loops.     #
  # Store the loss in loss and the gradient in dW. If you are not careful     #
  # here, it is easy to run into numeric instability. Don't forget the        #
  # regularization!                                                           #
  #############################################################################
  num_classes = W.shape[1]
  num_train = X.shape[0]
  loss = 0.0
  for i in range(num_train):
    scores = X[i].dot(W)
    #To remove numeric instability where there is a possibility of overflow,
    #we subtract maximum of the scores from each row
    scores = scores - np.max(scores) 
    correct_class_index = y[i]
    scores_e = np.exp(scores)
    scores_sum = np.sum(scores_e)
    loss += -1 * math.log(scores_e[correct_class_index]/scores_sum)

    for j in range(num_classes):
      if j != y[i]:
        dW[:,j] +=  X[i] * (scores_e[j]/ scores_sum) 

    dW[:,correct_class_index] += -1 * ((scores_sum - scores_e[correct_class_index])/scores_sum) *  X[i]


    
  # Right now the loss is a sum over all training examples, but we want it
  # to be an average instead so we divide by num_train.
  loss /= num_train

  # Add regularization to the loss.
  loss += reg * np.sum(W * W)

  #Averaging dW over all the training examples
  dW /= num_train

  #Adding regularization to dW
  dW += 2 * reg * W

  #############################################################################
  #                          END OF YOUR CODE                                 #
  #############################################################################

  return loss, dW


def softmax_loss_vectorized(W, X, y, reg):
  """
  Softmax loss function, vectorized version.

  Inputs and outputs are the same as softmax_loss_naive.
  """
  # Initialize the loss and gradient to zero.
  loss = 0.0
  dW = np.zeros_like(W)
  num_train = X.shape[0]

  #############################################################################
  # TODO: Compute the softmax loss and its gradient using no explicit loops.  #
  # Store the loss in loss and the gradient in dW. If you are not careful     #
  # here, it is easy to run into numeric instability. Don't forget the        #
  # regularization!                                                           #
  #############################################################################
  scores = X.dot(W)
  #To remove numeric instability where there is a possibility of overflow,
  #we subtract maximum of the scores from each row
  scores = scores - np.max(scores) 
  scores_e = np.exp(scores) #500*10
  actuals = scores_e[np.arange(num_train), y] # (500*1)
  scores_sum = np.sum(scores_e, axis = 1) #500*1
  ratios = np.log(np.divide(actuals, scores_sum))
  loss = -1 * np.sum(ratios)
  loss = loss/num_train
  # Add regularization to the loss.
  loss += reg * np.sum(W * W)


  scores_divided = (np.divide(scores_e.T, scores_sum)).T
  scores_divided[np.arange(num_train), y] -= 1
  dW = X.T.dot(scores_divided)
  dW = dW/num_train
  #Adding regularization to dW
  dW += 2 * reg * W
  
  #############################################################################
  #                          END OF YOUR CODE                                 #
  #############################################################################

  return loss, dW

