import matplotlib.pyplot as plt
import numpy as np

# read csv data from  output.csv
data = np.genfromtxt('/home/jan/Desktop/SICK Hackathon/output.csv', delimiter=',')

timestamp  = data[:, 0]
x = data[:, 1]
y = data[:, 2]

# plot the data
plt.figure()
plt.plot(x, y, 'r-')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.title('Position Data')
plt.show()
