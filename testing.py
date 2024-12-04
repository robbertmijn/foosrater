import matplotlib.pyplot as plt


with open("error.txt", 'r') as file:
    error = [float(line.strip()) for line in file]
    
# Create a figure and axis
plt.figure(figsize=(10, 6))

# Plot the numbers
plt.plot(error, marker='o', linestyle='-', label='Data')
plt.show()