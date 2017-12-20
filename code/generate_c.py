# https://deeplearningcourses.com/c/unsupervised-machine-learning-hidden-markov-models-in-python
# https://udemy.com/unsupervised-machine-learning-hidden-markov-models-in-python
# http://lazyprogrammer.me
# Generate continuous data from an HMM.
import numpy as np
import matplotlib.pyplot as plt


def simple_init():
    M = 1     # state
    K = 1    # Gaussian
    D = 1  #dimension
    pi = np.array([1])
    A = np.array([[1]])
    R = np.array([[1]])     # Responsibilities (prob of each individual gaussian)
    mu = np.array([[[0]]])
    sigma = np.array([[[[1]]]])
    return M, K, D, pi, A, R, mu, sigma

def big_init():
    """A more complex signal"""
    M = 5     # States
    K = 3     # Number of gaussians
    D = 2     # dimensions

    pi = np.array([1, 0, 0, 0, 0]) # initial state distribution

    A = np.array([
        [0.9, 0.025, 0.025, 0.025, 0.025],
        [0.025, 0.9, 0.025, 0.025, 0.025],
        [0.025, 0.025, 0.9, 0.025, 0.025],
        [0.025, 0.025, 0.025, 0.9, 0.025],
        [0.025, 0.025, 0.025, 0.025, 0.9],
    ]) # state transition matrix - likes to stay where it is (large prob to keep the state when transitioning)

    R = np.ones((M, K)) / K # mixture proportions (responsibilities)

    mu = np.array([
        [[0, 0], [1, 1], [2, 2]],
        [[5, 5], [6, 6], [7, 7]],
        [[10, 10], [11, 11], [12, 12]],
        [[15, 15], [16, 16], [17, 17]],
        [[20, 20], [21, 21], [22, 22]],
    ]) # M x K x D

    # Covariance matrix (defined as a circular gaussian, identity covariance)
    sigma = np.zeros((M, K, D, D))
    for m in xrange(M):
        for k in xrange(K):
            sigma[m,k] = np.eye(D)

    return M, K, D, pi, A, R, mu, sigma


def get_signals(N=20, T=100, init=big_init):
    """ This does all the sampling
        N : number of the sequences
        T : length of the sequences
    """
    M, K, D, pi, A, R, mu, sigma = init()

    X = []          # the data, the N x T
    for n in xrange(N):
        x = np.zeros((T, D))
        s = 0 # initial state is 0 since pi[0] = 1  (doesn't have to be this way!, It is like
                                                  #   so because the init functions above have all the prob mass
                                                  #   on the first stage.)
        r = np.random.choice(K, p=R[s]) # choose mixture
        x[0] = np.random.multivariate_normal(mu[s][r], sigma[s][r])
        for t in xrange(1, T):
            s = np.random.choice(M, p=A[s]) # choose state
            r = np.random.choice(K, p=R[s]) # choose mixture
            x[t] = np.random.multivariate_normal(mu[s][r], sigma[s][r])  # Return a D-dimensional array
        X.append(x)
    return X

if __name__ == '__main__':
    T = 500
    x = get_signals(1,T)[0]
    print x.shape
    axis = range(x.shape[0])
    plt.plot(axis, x[:, 0], axis, x[:, 1])
    plt.show()

