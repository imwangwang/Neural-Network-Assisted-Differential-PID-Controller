import numpy as np
from sklearn.metrics import mean_squared_error
import time

class MLP:

    def __init__(self,layers=1,n_nodes=10,eps=1e-9,bias=1,epochs=100,disp=False):
        self.layers = layers
        self.n_nodes = n_nodes
        self.eps = eps
        self.bias = bias
        self.epochs = epochs
        self.disp = disp

    def fprop(self, X, thetas):
        layers = self.layers
        n_nodes = self.n_nodes
        bias = self.bias

        r_x,c_x = X.shape
        r_y = self.r_y
        c_y = self.c_y

        X_bias = np.c_[(np.ones(r_x)*bias).T, X]

        # forward prop
        # input to first layer
        ind_start = 0
        ind_end = (c_x + 1) * n_nodes
        theta = thetas[ind_start:ind_end]
        theta = theta.reshape((c_x+1,n_nodes))
        a = np.dot(X_bias,theta)

        # pass outputs through activation function
        a = np.tanh(a)

        # loop through rest of layers
        for i in xrange(layers - 1):
            ind_start = ind_end
            ind_end += (n_nodes + 1) * n_nodes
            theta = thetas[ind_start:ind_end]
            theta = theta.reshape((n_nodes+1, n_nodes))
            a_bias = np.c_[(np.ones(r_x)*bias).T, a]
            a = np.dot(a_bias, theta)
            a = np.tanh(a)

        # last layer to output
        ind_start = ind_end
        ind_end += (n_nodes + 1) * c_y
        a_bias = np.c_[(np.ones(r_x)*bias).T, a]
        theta = thetas[ind_start:ind_end]
        theta = theta.reshape((n_nodes+1, c_y))

        outputs = np.dot(a_bias, theta)

        return outputs

    def train(self, X, y):
        layers = self.layers
        n_nodes = self.n_nodes
        eps = self.eps
        bias = self.bias
        epochs = self.epochs
        disp = self.disp

        r_x,c_x = X.shape
        r_y,c_y = y.shape

        self.r_x = r_x
        self.c_x = c_x
        self.r_y = r_y
        self.c_y = c_y

        N = ((c_x+1)*n_nodes) + ((n_nodes+1)*n_nodes*(layers-1)) + (n_nodes+1)*c_y
        thetas = np.random.rand(N)
        outputs = np.zeros(y.shape)
        nP = outputs.shape[0]*outputs.shape[1]
        rho = 1
        rho = rho * np.eye(N)

        cost_prev = 0

        for ep in xrange(epochs):
            if disp:
                print "===================EPOCH %d===================" %(ep)
                t = time.time()
            orig_err = []
            orig_outputs = []
            j_thetas = np.copy(thetas)
            jacobian = np.zeros((nP,N))
            # calculate jacobian error values
            for j_ind in xrange(N+1):
                # print j_ind
                # increment a different theta for each iteration
                if j_ind != 0:
                    j_thetas[j_ind-1] += eps
                    # undo previous eps increment
                    if j_ind != 1:
                        j_thetas[j_ind-1-1] -= eps

                # forward prop
                outputs = self.fprop(X, j_thetas)

                # calculate error matrix
                err = y - outputs
                err = err.reshape((err.shape[0]*err.shape[1],1))
                if j_ind == 0:
                    orig_err = np.copy(err)
                    orig_outputs = np.copy(outputs)
                else:
                    jacobian[:,j_ind-1] = err.reshape((err.shape[0],))
            # compute jacobian matrix
            jacobian = (jacobian - orig_err) / eps
            ainv = np.linalg.inv(rho + np.dot(jacobian.T,jacobian))
            thetas = thetas - (np.dot(ainv, np.dot(jacobian.T,orig_err))).reshape((thetas.shape[0],))

            cost = mean_squared_error(y,orig_outputs)

            if disp:
                print "Cost =", cost
                print "time =", (time.time() - t)

            if abs(cost - cost_prev) < 1e-6:
                break
            else:
                cost_prev = cost
        self.thetas = thetas

    def predict(self, X):
        return self.fprop(X, self.thetas)

if __name__ == "__main__":
    filename = "data.txt"
    data = np.loadtxt(filename, delimiter=' ')
    X_orig = data[:,:5]
    y_orig = data[:,5:]

    X_mean = np.mean(X_orig, axis=0)
    y_mean = np.mean(y_orig, axis=0)
    X_std = np.std(X_orig, axis=0)
    y_std = np.std(y_orig, axis=0)

    X = X_orig - X_mean
    X = X / X_std
    y = y_orig - y_mean
    y = y / y_std

    use = 1100
    X = X[:use,:]
    y = y[:use,:]

    mlp = MLP(n_nodes=10,layers=1,epochs=100)
    mlp.train(X,y)
    y_pred = mlp.predict(X)

    print mean_squared_error(y,y_pred)

    for i in xrange(3):
        print i,y_pred[i,:10]
        print i,y[i,:10]
