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
#Defining function to normalize irradiances.
def irrNorm(a_list):
emp = []
for k in a_list:
k = k/1000
emp.append(k)
return emp
x_labels = [f"July {n}" for n in range(1,32)]
i=1

nk = 0
for ax in axs:
input_file = f"2024-07-{i:02}.csv"
sort = sort_csv(input_file, sort_column)
dateTime = sort["Date_Time"].tolist()
tm = exDT(dateTime)
tm = tchange(tm)
ones_list = np.ones(len(tm), dtype=int).tolist()
tempA = sort["Temperature_Ambient"].tolist() #Ambient Temp
pyro7F3 = sort["Irradiance_before_Pyranometer CMP3"].tolist()
pyro7F3 = irrNorm(pyro7F3)
ax.plot(tm, pyro7F3, c = "red")
ax.plot(tm,ones_list,"k--")
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_xlabel(x_labels[nk] if nk < len(x_labels) else '', fontsize = 8)
ax.set_ylim(0,1.2)
ax.set_xticks([])
ax.set_yticks([])
ax.minorticks_off()
if i == 1 or i == 17: # First subplot (0) and 17th subplot (16)
single_tick = 1 # Example position for the single tick, adjust as needed
ax.set_yticks([single_tick])
ax.set_yticklabels(['1000 W/m$\mathregular{^{2}}$'], rotation = 'vertical',
verticalalignment='center')
i=i+1
nk = nk +1
if i==32:
break
# Set the overall title for the figure
fig.suptitle('Irradiation, July 2024', fontsize=22, fontweight = "bold")
# Set the x and y axis labels for the entire figure
fig.text(0.5, 0.04, 'Time of the Day', ha='center', va='center', fontsize=17)
fig.text(0.06, 0.5, 'Normalized Irradiance (POA)', ha='center', va='center', rotation='vertical',
fontsize=17)

axs[-1].set_visible(False)
plt.savefig("ir1")
plt.close()
