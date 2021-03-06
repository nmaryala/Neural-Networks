from builtins import range
from builtins import object
import numpy as np

from cs682.layers import *
from cs682.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        self.params['W1'] = weight_scale * np.random.randn(input_dim, hidden_dim)
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['W2'] = weight_scale * np.random.randn(hidden_dim, num_classes)
        self.params['b2'] = np.zeros(num_classes)

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        reg = self.reg
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        intermediate, cache1 = affine_relu_forward(X, W1, b1)
        scores, cache2 = affine_relu_forward(intermediate, W2, b2)
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        num_train = X.shape[0]
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        grads['W1'] = np.zeros_like(W1)
        grads['W2'] = np.zeros_like(W1)
        grads['b1'] = np.zeros_like(b1)
        grads['b2'] = np.zeros_like(b2)

        loss, grad = softmax_loss(scores, y)
        reg_loss = reg * np.sum(W1 * W1) +  reg * np.sum(W2 * W2)
        loss = loss + 0.5*reg_loss

        dx_intermediate, dw_intermediate, db_intermediate = affine_relu_backward(grad, cache2)
        dx, dw, db = affine_relu_backward(dx_intermediate, cache1)

        grads['b2'] = db_intermediate
        grads['b1'] = db
        grads['W2'] = dw_intermediate + W2*reg
        grads['W1'] = dw + W1*reg  
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        dim_list = []
        dim_list.append(input_dim)
        dim_list += hidden_dims
        dim_list.append(num_classes)

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        
        for i in range(1, self.num_layers + 1):
            self.params['W'+str(i)] = weight_scale * np.random.randn(dim_list[i-1] ,dim_list[i])
            self.params['b'+str(i)] = np.zeros(dim_list[i])


        if self.normalization=='batchnorm' or self.normalization=='layernorm':
            for i in range(1, self.num_layers):
                self.params['gamma'+str(i)] = np.ones(dim_list[i])
                self.params['beta'+str(i)] = np.zeros(dim_list[i])

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization=='batchnorm':
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]
        if self.normalization=='layernorm':
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization=='batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None

        caches = []
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        X_current = X
        for i in range(1, self.num_layers):
            if self.normalization == 'batchnorm' or self.normalization == 'layernorm':
               intermediate, cache = affine_norm_relu_forward(X_current, self.params["W"+str(i)], self.params["b"+str(i)], self.params['gamma'+str(i)], self.params['beta'+str(i)], self.bn_params[i-1], self.normalization, self.use_dropout, self.dropout_param)
            else:
               intermediate, cache = affine_relu_forward(X_current, self.params["W"+str(i)], self.params["b"+str(i)])
            caches.append(cache)
            X_current = intermediate


        intermediate, cache = affine_forward(X_current, self.params["W"+str(i+1)], self.params["b"+str(i+1)])
        caches.append(cache)
        X_current = intermediate
        scores = X_current

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, grad = softmax_loss(scores, y)
        reg_loss = 0
        for i in range(1, self.num_layers + 1):
            reg_loss += np.sum(self.params["W"+str(i)]*self.params["W"+str(i)])  
        loss = loss + 0.5*reg_loss*self.reg

        grad_current = grad
        grad_current, dw_intermediate, db_intermediate = affine_backward(grad_current, caches[-1])
        grads["W"+str(i)] = dw_intermediate + self.params["W"+str(i)]*self.reg
        grads["b"+str(i)] = db_intermediate

        for i in range(2, self.num_layers + 1):
            if self.normalization == 'batchnorm' or self.normalization == 'layernorm':
              dx_intermediate, dw_intermediate, db_intermediate, dgamma, dbeta = affine_norm_relu_backward(grad_current, caches[-i], self.normalization, self.use_dropout)
              grads['gamma'+str(self.num_layers + 1 - i)] = dgamma
              grads['beta' +str(self.num_layers + 1 - i)] = dbeta
            else:
              dx_intermediate, dw_intermediate, db_intermediate = affine_relu_backward(grad_current, caches[-i])
            grads["W"+str(self.num_layers + 1 - i)] = dw_intermediate + self.params["W"+str(self.num_layers + 1 - i)]*self.reg
            grads["b"+str(self.num_layers + 1 - i)] = db_intermediate
            grad_current = dx_intermediate
            

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads

def affine_norm_relu_forward(x, w, b, gamma, beta, bn_param, normalization, dropout, dropout_param):
    """
    Convenience layer that perorms an affine transform followed by normalization followed by a ReLU

    Inputs:
    - x: Input to the affine layer
    - w, b: Weights for the affine layer
    - gamma, beta, bn_param: parameters for normalization layer
    - normalization: Type of normalization
    - dropout: dropout bool
    - dropout_param: parameters for dropout

    Returns a tuple of:
    - out: Output from the ReLU
    - cache: Object to give to the backward pass
    """
    bn_cache, do_cache = None, None
   
    a, fc_cache = affine_forward(x, w, b)

    if normalization == 'batchnorm':
        a, bn_cache = batchnorm_forward(a, gamma, beta, bn_param)
    if normalization == 'layernorm':
        a, bn_cache = layernorm_forward(a, gamma, beta, bn_param)

    a, relu_cache = relu_forward(a)

    if dropout:
        a, do_cache = dropout_forward(a, dropout_param)

    cache = (fc_cache, bn_cache, relu_cache, do_cache)
    return a, cache


def affine_norm_relu_backward(dout, cache, normalization, dropout):
    """
    Backward pass for the affine-norm-relu convenience layer
    """
    fc_cache, bn_cache, relu_cache, do_cache = cache

    if dropout:
        dout = dropout_backward(dout, do_cache)

    dout = relu_backward(dout, relu_cache)

    dgamma, dbeta = None, None
    if normalization == 'batchnorm':
        dout, dgamma, dbeta = batchnorm_backward_alt(dout, bn_cache)
    if normalization == 'layernorm':
        dout, dgamma, dbeta = layernorm_backward(dout, bn_cache)

    dx, dw, db = affine_backward(dout, fc_cache)
    return dx, dw, db, dgamma, dbeta

