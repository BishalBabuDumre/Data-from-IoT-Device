import csv
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

#Creating Bold Graph Edges and Fonts
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 14

# Open the CSV file for reading
with open('2024-09-25.csv', mode='r') as file:
    # Create a CSV reader with DictReader
    csv_reader = csv.DictReader(file)
 
    # Initialize an empty list to store the dictionaries
    data_list = []
 
    # Iterate through each row in the CSV file
    for row in csv_reader:
        # Append each row (as a dictionary) to the list
        data_list.append(row)
 
# Print the list of dictionaries
b = 0
for data in data_list:
    pv = float(data["Vpeak"])
    pc = float(data["Ipeak"])
    c = float(data["Isc"])
    v = float(data["Voc"])
    x = data["volts_curve"]
    y = data["amps_curve"]
    z = data["Date_Time"]
    n = data["Name"]
    x = x[1:]
    x = x[:(len(x)-1)]
    y = y[1:]
    y = y[:(len(y)-1)]
    plt.figure(figsize=(7,5))
    x = list(x.split(","))
    y = list(y.split(","))    
    a = 0
    for i in x:
        x[a] = float(x[a])
        y[a] = float(y[a])
        a+=1
    plt.plot(x,y, c = 'k')
    plt.plot(0,c, c = 'b', marker = 'o', markersize = 20)
    plt.plot(v,0, c = 'g', marker = 'X', markersize = 20)
    plt.plot(pv,pc, c = 'r', marker = 'P', markersize = 20)
    plt.title(n+', '+z)
    plt.xlim(x[0]-0.02,x[len(x)-1]+0.05)
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current in Circuit (A)")
    plt.savefig('Fig-{0}.png'.format(b))
    b+=1
