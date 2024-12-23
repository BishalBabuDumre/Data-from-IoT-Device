import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
import pandas as pd
from datetime import date
from datetime import datetime
import numpy as np
#Creating Bold Graph Edges and Fonts
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5
#Sort the CSV
def sort_csv(input_file, sort_column):
# Read the CSV file into a DataFrame
df = pd.read_csv(input_file)
# Sort the DataFrame based on the specified column
df_sorted = df.sort_values(by=sort_column)
return df_sorted
#Extract only Times from the DateTime
def exDT(dateTime):
aList = []
start_index = 11
end_index = 16
for original_string in dateTime:
selected_section = original_string[start_index:end_index]
aList.append(selected_section)
return aList
def tchange(tList):
time_format = "%H:%M"
k = []
for j in tList:
a = datetime.strptime(j, time_format)
k.append(a)
return k
sort_column = 'Date_Time' # Specify the column you want to sort by
fig, axs = plt.subplots(nrows=2, ncols=16, figsize=(9, 6.5))
axs = axs.flatten()
x_labels = [f"July {n}" for n in range(1,32)]
i=1
nk = 0
for ax in axs:
input_file = f"2024-07-{i:02}.csv"
sort = sort_csv(input_file, sort_column)
dateTime = sort["Date_Time"].tolist()
tm = exDT(dateTime)
tm = tchange(tm)
array1 = np.full(len(tm), 20).tolist()

array2 = np.full(len(tm), 30).tolist()
array3 = np.full(len(tm), 40).tolist()
tempA = sort["Temperature_Ambient"].tolist() #Ambient Temp
ax.plot(tm, tempA, c = "blue")
ax.plot(tm,array1,"k--")
ax.plot(tm,array2,"k--")
ax.plot(tm,array3,"k--")
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_xlabel(x_labels[nk] if nk < len(x_labels) else '', fontsize = 8)
ax.set_ylim(12, 45)
ax.set_xticks([])
ax.set_yticks([])
ax.minorticks_off()
if i == 1 or i == 17: # First subplot (0) and 17th subplot (16)
ax.set_yticks([20, 30, 40])
ax.set_yticklabels(['20 $\mathregular{^{o}}C$', '30 $\mathregular{^{o}}C$', '40
$\mathregular{^{o}}C$'], rotation = 'vertical', verticalalignment='center')
i=i+1
nk = nk +1
if i==32:
break
# Set the overall title for the figure
fig.suptitle('Temperature, July 2024', fontsize=22, fontweight = "bold")
# Set the x and y axis labels for the entire figure
fig.text(0.5, 0.04, 'Time of the Day', ha='center', va='center', fontsize=17)
fig.text(0.06, 0.5, 'Ambient Temperature', ha='center', va='center', rotation='vertical', fontsize=17)

axs[-1].set_visible(False)
plt.savefig("te1")
plt.close()
