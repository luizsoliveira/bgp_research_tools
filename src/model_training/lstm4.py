# -*- coding: utf-8 -*-
"""
Originally based on:
    https://github.com/zhida-li/CyberDefense/blob/main/src/RNN_Running_Code/RNN_Run/code_template/lstm_4layer.py
"""
######################################################
##### LSTM4 (4 hidden layers) using BGP datasets #####
######################################################
# Import the Python libraries
import time

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
import torch.utils.data as Data
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
import os
import sys

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from dataset.dataset import Dataset

# Set the seed for generating random numbers on all GPUs.
torch.manual_seed(1)  
torch.cuda.manual_seed_all(1)

### Hyper parameters ####
num_feature = 37    # number of the features for input matrix
# batch_size = 5
# batch_size = 10
batch_size = 20
sequence_length = batch_size     # length of the input time sequence
input_size = num_feature
input_lstm = num_feature
hidden_size = 80    # hidden size for fc3
hidden_size2 = 32   # hidden size for fc35
hidden_size3 = 16   # hidden size for fc4
num_layers = 1      # number of layers for LSTM algorithm
num_classes = 2     # number of the class
num_epochs = 30     # number of the epochs
learning_rate = 0.001    # learning rate for optimization

# Load the datasets, x: data, y: label
dataset = Dataset("/var/netscience/tasks/c69ff6eb-de0a-49eb-92e9-63a51210a499/DATASET.csv")
dataset = dataset.get_normalized_zscore_dataset()

train_dataset, test_dataset = dataset.get_train_test_datasets_anomalous_ratio(0.60)

train_x, train_y = train_dataset.get_x_y()

test_x, test_y = test_dataset.get_x_y()

print(train_x.shape)
print(train_y.shape)

print(test_x.shape)
print(test_y.shape)

test_len = len(test_y)

# Convert numpy to torch tensor
train_data_x, train_label_y = torch.from_numpy(train_x), torch.from_numpy(train_y)
test_data_x, test_label_y = torch.from_numpy(test_x), torch.from_numpy(test_y)

# Tensor
train_data,test_data = train_data_x.type(torch.FloatTensor), test_data_x.type(torch.FloatTensor)   # FloatTensor = 32-bit floating
train_label,test_label = train_label_y.type(torch.LongTensor),test_label_y.type(torch.LongTensor)  # LongTensor = 64-bit integer

# Data loader (input pipeline)
torch_dataset_train = Data.TensorDataset(train_data,train_label)
torch_dataset_test = Data.TensorDataset(test_data,test_label)

train_loader = Data.DataLoader(dataset=torch_dataset_train,  # torch TensorDataset format
                               batch_size=batch_size,
                               shuffle=False)

test_loader = Data.DataLoader(dataset=torch_dataset_test,
                              batch_size=batch_size,
                              shuffle=False)

#### Build the deep learning models with 2 hidden layers (one layer: LSTM, three layer: fc3, fc35, and fc4) ###
class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Define the LSTM module
        self.lstm = nn.LSTM(input_lstm, hidden_size, num_layers, batch_first=False, dropout=0.4)

        # Define ReLU layer
        self.relu = nn.ReLU()

        # Define the Dropout layer with 0.5 dropout rate
        self.keke_drop = nn.Dropout(p=0.5)

        # Define a fully-connected layer fc3 with 80 inputs and 32 outputs
        self.fc3 = nn.Linear(hidden_size, hidden_size2)

        # Define a fully-connected layer fc35 with 32 inputs and 16 outputs
        self.fc35 =  nn.Linear(hidden_size2, hidden_size3)

        # Define a fully-connected layer f4 with 16 inputs and 2 outputs
        self.fc4 = nn.Linear(hidden_size3, num_classes)

    def forward(self, x):
        # Set initial states: h_0 (num_layers * num_directions, batch, hidden_size)
        # x=input (seq_len, batch, input_size)
        if torch.cuda.is_available():
            h0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size).cuda())
            c0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size).cuda())
        else:
            h0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size).cpu())
            c0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size).cpu())


        x, _ = self.lstm(x, (h0, c0))  # LSTM network, c is the state

        x = self.relu(self.fc3(x))     # fully-connected layer with ReLU()

        x = self.keke_drop(x)
        x = self.relu(self.fc35(x))    # fully-connected layer with ReLU()
        x = self.keke_drop(x)
        x = self.fc4(x)                # fully-connected layer
        return x

rnn = RNN()
start = time.perf_counter()
rnn.train()

if torch.cuda.is_available():
    rnn.cuda()
else:
    rnn.cpu()

# Select criterion for loss
criterion = nn.CrossEntropyLoss()

# Select an optimizer
optimizer = torch.optim.RMSprop(rnn.parameters(), lr=learning_rate)           # or Adam 

print ("batch size : " , batch_size)
print ("test_len : " , test_len)
print ("hidden_size1 : " , hidden_size)
print ("hidden_size2 : " , hidden_size2)
print ("hidden_size3 : " , hidden_size3);


start = time.time()

### Train the model ###
for epoch in range(num_epochs):
    for i, (train, labels) in enumerate(train_loader):                        # load the data
        #The last batch will have a size less than sequence_length
        batch_size_on_this_sample = train.shape[0]
        if torch.cuda.is_available():
            x = Variable(train.view(batch_size_on_this_sample, -1, input_lstm)).cuda()      # reshape x to (time_step, batch, input_size)
            y = Variable(labels).cuda()                                           # batch labels
        else:
            x = Variable(train.view(batch_size_on_this_sample, -1, input_lstm)).cpu()      # reshape x to (time_step, batch, input_size)
            y = Variable(labels).cpu()                                           # batch labels

        # Forward + Backward + Optimize
        outputs = rnn(x)                                                      # RNN output
        outputs = outputs.view(-1, 2)
        loss = criterion(outputs, y)                                          # cross entropy loss
        optimizer.zero_grad()                                                 # clear gradients for this training step
        loss.backward()                                                       # back-propagation: compute gradients
        optimizer.step()                                                      # apply gradients


end = time.perf_counter()


### Test the model using evaluation mode ###
correct = 0
total = 0

rnn.eval()          # evaluation mode for testing
yo = []
new_yo=[]
for i, (test, l) in enumerate(test_loader):
    #The last batch will have a size less than sequence_length
    batch_size_on_this_sample = test.shape[0]
    if torch.cuda.is_available():
        p = Variable(test.view(batch_size_on_this_sample, -1, input_lstm)).cuda()
    else:
        p = Variable(test.view(batch_size_on_this_sample, -1, input_lstm))
    
    #Checking inhomogeneous
    # if len(p) < batch_size:
    #     continue
    
    # print(i, p)
    outputs2 = rnn(p)
    outputs2 = outputs2.view(-1, 2)
    outputs2 = F.softmax(outputs2)     # softmax function
    # print 'output2 size:', outputs2.size()
    _, predicted = torch.max(outputs2.data, 1)
    total += l.size(0)  # l.size(0)=100
    
    #Changed
    if torch.cuda.is_available():
        predicted = predicted.cpu()
    # else:
    #     predicted = predicted.cpu()
    
    correct += (predicted == l).sum()
    predicted_np = predicted.numpy()
    # yo.append(predicted_np) # predicted labels, yo shape is (1, 72, 100, 1)
    yo.extend(predicted_np)
    


# yo = np.array([yo]).reshape(test_len, -1)
yo = np.array(yo).reshape(-1)
yo_test = test_label_y.numpy()
# To do: remove this 
# yo_test = yo_test[:len(yo)]
acc = accuracy_score(yo_test, yo)
fScore = f1_score(yo_test, yo)


# Save the accuracy and F-Score
with open("accuracy.txt", "w") as text_file:
    text_file.write("Accuracy: %.4f, Fscore %.4f" % (acc*100, fScore*100))


# Save the running time
with open("runtime.txt", "w") as text_file:
    text_file.write("Run Time: %.4f" % (end-start))

model_pkl = 'rnn-lstm4-%d' % sequence_length
torch.save(rnn.state_dict(), '%s.pkl'%model_pkl)
