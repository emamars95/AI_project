# -*- coding: utf-8 -*-
"""fitting_with_KRR_colab.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/maxjr82/MLinQCbook22-KMs/blob/master/CECAM/fitting_with_KRR_colab.ipynb

# **Fitting with KRR**

<table align="left"><td>
  <a target="_blank"  href="https://colab.research.google.com/github/maxjr82/MLinQCbook22-KMs/blob/master/CECAM/fitting_with_KRR_colab.ipynb">
    <img src="https://www.tensorflow.org/images/colab_logo_32px.png" />Run in Google Colab
  </a>
</td><td>
  <a target="_blank"  href="https://github.com/maxjr82/MLinQCbook22-KMs/blob/master/CECAM/fitting_with_KRR_colab.ipynb">
    <img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" />View source on GitHub</a>
</td></table>
"""

# download necessary files if not exist
! wget https://raw.githubusercontent.com/maxjr82/MLinQCbook22-KMs/master/notebooks/R_20.dat
! wget https://raw.githubusercontent.com/maxjr82/MLinQCbook22-KMs/master/notebooks/E_FCI_20.dat
! wget https://raw.githubusercontent.com/maxjr82/MLinQCbook22-KMs/master/notebooks/R_451.dat
! wget https://raw.githubusercontent.com/maxjr82/MLinQCbook22-KMs/master/notebooks/E_FCI_451.dat
! wget https://raw.githubusercontent.com/maxjr82/MLinQCbook22-KMs/master/notebooks/itrain.dat
! wget https://raw.githubusercontent.com/maxjr82/MLinQCbook22-KMs/master/notebooks/itest.dat

import numpy as np
import matplotlib.pyplot as plt

"""# define KRR class and formula explanation

## KRR class

**lambda_** defines the hyperparameter $\lambda$   
**sigma** defines the hyperparameter $\sigma$   
kernel can be 'Linear' or 'Gaussian'   
use method **fit(X, y)** to train a model   
 - X: size (N, p), N data, p dimension  
 - y: size (N, 1), N data  
 - you can use **arr.reshape(-1, 1)** to reshape y variable  
 
ues method **predict(X)** to make prediction with given X  
 - return y: size (N, 1) 


## training formula:

$$ \alpha = (K + \lambda I)^{-1} \boldsymbol{y} $$  
the size of $\alpha$ is: (N, 1)  
where K is $K=k(x_i, x_j)$,  
I is the identity matrix with the same size with K  
y is the target value, size (N, 1)  


## prediction formula:

$$ y^{*} = K^{*} \alpha  $$  
$K^{*}$ is the kernel matrix $K(x_{test}, x_{train})$  
the result $y^{*}$ is the has the size (N_test, 1)
"""

class KRR():
    def __init__(self, kernel='Linear', lambda_=0.1, **kw):
        self.kernel = getattr(self, kernel)
        self.params = {'lambda': lambda_, 'sigma': 0.01}
        for k, v in kw.items():
            self.params[k] = v
        self.train_x = None
        self.alpha = None
    
    def Linear(self, x1, x2):
        return x1 @ x2.T
    
    def Gaussian(self, x1, x2):
        dist = np.sum(x1**2, 1).reshape(-1, 1) \
               + np.sum(x2**2, 1) \
               - 2*np.dot(x1, x2.T)
        return np.exp(-0.5 * dist / (self.params['sigma']**2))
    
    def fit(self, X, y):
        self.train_x = np.asarray(X)
        self.train_y = np.asarray(y).reshape(-1, 1)
        K = self.kernel(self.train_x, self.train_x)
        self.alpha = np.linalg.inv(K + self.params['lambda'] * np.eye(len(self.train_x))) @ self.train_y
    
    def predict(self, X):
        self.pred_x = np.asarray(X)
        K = self.kernel(self.pred_x, self.train_x)
        return K @ self.alpha

"""# Training KRR with the linear kernel"""

# load FCI 20 points data for H2
x = np.loadtxt('R_20.dat')
y = np.loadtxt('E_FCI_20.dat')

x, y # let's check the data

# define a KRR model with linear kernel.
krr = KRR(kernel='Linear', lambda_=0.000001)  
# fit train this model with data
krr.fit(x.reshape(-1, 1), y.reshape(-1, 1))

# make prediction, 100 points ranging from 0.5 to 5
test_x = np.linspace(0.5, 5, 100) 
test_y = krr.predict(test_x.reshape(-1, 1))

# plot the result
plt.plot(test_x, test_y.ravel(), label='prediction')
plt.plot(x, y, 'ro', label='training data')
plt.title('KRR trained with E_FCI_20 data and Linear kernel')
plt.xlabel('R, $\mathrm{\AA}$'); plt.ylabel('E_FCI, Hartree')
plt.legend()

"""# Training KRR with the Gaussian kernel"""

# load data with FCI 451 points for H2
x = np.loadtxt('R_451.dat')
y = np.loadtxt('E_FCI_451.dat')
# load the index for train and test data set
train_idx = np.loadtxt('itrain.dat', dtype=np.int64) - 1
test_idx = np.loadtxt('itest.dat', dtype=np.int64) - 1

train_idx, test_idx # let's check the index

# get train & test data through index
train_x, train_y = x[train_idx], y[train_idx]
test_x, test_y = x[test_idx], y[test_idx]

# define a KRR model with linear kernel, and trian it
krr = KRR(kernel='Gaussian', sigma=1, lambda_=3.5e-13)
krr.fit(train_x.reshape(-1, 1), train_y.reshape(-1, 1))

# make prediction
pred_y = krr.predict(test_x.reshape(-1, 1))

# plot the result
plt.plot(test_x, pred_y.ravel(), label='prediction')
plt.plot(x, y, lw=10, alpha=0.3, label='groud truth')
plt.plot(train_x, train_y, 'ro', label='training data')
plt.title('KRR trained with E_FCI_451 data and Gaussian kernel')
plt.xlabel('R, $\mathrm{\AA}$'); plt.ylabel('E_FCI, Hartree')
plt.legend()