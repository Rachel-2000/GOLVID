import matplotlib.pyplot as plt
import matplotlib.ticker as tk

# plt.boxplot([LenMa, Spell, Drain, Logram, LogPPT, LogDiv], labels=['Lenma', 'Spell', 'Drain', 'Logram', 'LogPPT', 'LogDiv'], 
#                         showmeans=True, medianprops={'color':'#913226'}, meanprops={'markerfacecolor':'#3F76B1', 'markeredgecolor':'none'})

# PA

LenMa = [72.2, 29.3, 15.4, 24.2, 12.5, 28.9, 67.1, 13.2, 15.5, 15.5, 19.1, 50.6, 2.3, 17.1, 26.6, 45.7]
Spell = [24.1, 28.5, 32.9, 19.6, 48.7, 15.2, 53.2, 10.9, 3.3, 12.7, 0.0, 47.8, 33.6, 3.9, 0.4, 45.3]
Drain = [95.9, 43.9, 37.6, 49.8, 44.4, 67.2, 19.1, 69.6, 19.4, 73.0, 24.1, 100, 52.7, 53.4, 18.7, 27.7]
Logram = [42.8, 50.9, 17.0, 37.0, 1.8, 26.3, 67.9, 18.5, 25.2, 48.2, 11.2, 0.0, 27.5, 12.8, 37.4, 51.6]
LogPPT = [76.70, 99.40, 97.00, 89.50, 90.20, 78.90, 94.70, 94.90, 67.30, 97.60, 90.70, 100.00, 99.10, 92.60, 98.30, 99.00]
LogDiv = [93.83, 100.00, 98.17, 99.33, 99.89, 99.61, 97.94, 99.72, 84.94, 93.94, 99.78, 100.00, 99.94, 96.78, 100.00, 100.00]

plt.title('Distribution of Parsing Accuracy (%)')
plt.boxplot([LenMa, Spell, Drain, Logram, LogPPT, LogDiv], labels=['Lenma', 'Spell', 'Drain', 'Logram', 'LogPPT', 'LogDiv'], showmeans=True)
plt.grid(axis='y', linestyle='--')
plt.show()


# PTA

LenMa = [59.0, 42.9, 9.6, 20.6, 37.5, 3.4, 12.9, 41.0, 14.6, 25.0, 18.7, 10.6, 12.4, 27.1, 37.9, 30.0]
Spell = [24.4, 25.0, 12.1, 20.8, 57.1, 21.5, 38.3, 17.3, 5.7, 25.0, 0.0, 22.2, 34.5, 19.1, 11.5, 22.0]
Drain = [56.6, 100.0, 33.9, 36.8, 81.3, 8.3, 38.8, 43.4, 21.2, 52.0, 5.5, 26.9, 50.0, 29.9, 46.3, 39.1]
Logram = [38.7, 33.3, 15.7, 18.7, 19.4, 3.5, 37.7, 13.5, 16.4, 29.0, 9.3, 0.0, 3.1, 20.8, 15.2, 26.1]
LogPPT = [85.70, 54.00, 60.00, 74.10, 68.60, 73.60, 50.60, 55.40, 47.50, 58.40, 85.30, 83.30, 100.00, 48.90, 84.40, 43.60]
LogDiv = [84.62, 100.00, 85.71, 91.49, 81.82, 95.00, 73.53, 95.00, 58.78, 94.74, 95.00, 100.00, 88.24, 65.67, 100.00, 100.00]

plt.title('Distribution of Precision Template Accuracy (%)')
plt.boxplot([LenMa, Spell, Drain, Logram, LogPPT, LogDiv], labels=['Lenma', 'Spell', 'Drain', 'Logram', 'LogPPT', 'LogDiv'], showmeans=True)
plt.grid(axis='y', linestyle='--')
plt.show()

# RTA

LenMa = [60.1, 50.0, 25.8, 28.9, 42.9, 46.7, 50.0, 41.4, 19.4, 23.1, 60.5, 87.5, 33.3, 34.2, 44.0, 36.0]
Spell = [27.2, 16.7, 12.5, 23.7, 57.1, 18.7, 39.1, 14.7, 5.9, 23.1, 0.0, 25.0, 27.8, 16.8, 12.0, 26.0]
Drain = [62.0, 100.0, 30.8, 34.2, 92.9, 34.7, 41.3, 42.2, 24.9, 50.0, 39.5, 87.5, 41.7, 36.9, 50.0, 36.0]
Logram = [27.2, 83.3, 16.7, 17.5, 42.9, 25.3, 43.5, 4.3, 20.2, 34.6, 9.3, 0.0, 22.2, 6.7, 10.0, 24.0]
LogPPT = [85.70, 58.80, 58.30, 86.00, 78.30, 84.80, 59.10, 72.00, 49.10, 68.40, 85.30, 83.30, 100.00, 84.60, 88.40, 53.40]
LogDiv = [83.81, 100.00, 86.75, 95.56, 90.00, 95.00, 89.29, 90.48, 61.65, 90.00, 95.00, 100.00, 88.24, 86.27, 100.00, 100.00]

plt.title('Distribution of Recall Template Accuracy (%)')
plt.boxplot([LenMa, Spell, Drain, Logram, LogPPT, LogDiv], labels=['Lenma', 'Spell', 'Drain', 'Logram', 'LogPPT', 'LogDiv'], showmeans=True)
plt.grid(axis='y', linestyle='--')
plt.show()

# GA
LenMa = [99.8, 66.7, 86.9, 89.4, 31.6, 68.1, 94.3, 28.7, 23.8, 77.8, 16.6, 98.4, 49.5, 92.7, 21.3, 64.8]
Spell = [100.0, 53.3, 92.0, 98.7, 85.0, 65.7, 85.6, 99.0, 16.2, 89.1, 96.1, 30.1, 52.7, 48.8, 24.5, 72.4]
Drain = [99.8, 94.8, 90.5, 96.7, 95.5, 74.1, 96.0, 99.4, 42.2, 76.5, 64.4, 100.0, 52.7, 99.6, 22.4, 71.1]
Loggram = [1.2, 28.3, 28.2, 72.4, 21.8, 74.2, 12.9, 69.4, 20.1, 67.7, 25.8, 29.7, 1.6, 34.3, 24.1, 55.1]
LogPPT = [100.0, 99.4, 99.9, 95.4, 94.3, 67.9, 99.1, 93.4, 88.8, 100.0, 100.0, 100.0, 62.8, 98.9, 78.0]
LogDiv = [89.0, 82.0, 96.4, 100.0, 99.4, 94.8, 81.4, 99.2, 100.0, 72.8, 89.4, 100.0, 100.0, 95.8, 100.0, 98.1]
plt.title('Distribution of Grouping Accuracy (%)')
plt.boxplot([LenMa, Spell, Drain, Logram, LogPPT, LogDiv], labels=['Lenma', 'Spell', 'Drain', 'Logram', 'LogPPT', 'LogDiv'], showmeans=True)
plt.grid(axis='y', linestyle='--')
plt.show()
plt.savefig("GA.png")

# Example Number

x = [1, 3, 5, 7, 9]
PA = [75.9,	84.4,	84.9, 81.8, 81.9]
PTA = [56.0, 58.8, 59.1, 59.6, 60.9]
RTA = [51.1, 61.7, 62.4, 58.3, 56.8]

plt.figure(figsize=(6, 4))
plt.plot(x, PA, label='PA', color='#3F76B1', marker='o', linestyle='-.')
plt.plot(x, PTA, label='PTA', color='#913226', marker='v', linestyle='--')
plt.plot(x, RTA, label='RTA', color='#913226', marker='^', linestyle=':')
plt.xticks(x)
plt.title('Analysis of Example Number (%)')
plt.legend()
plt.grid(axis='x', linestyle='--')
plt.show()

# Permutation Method
import numpy as np
labels = ['PA', 'PTA', 'RTA']
x = np.arange(len(labels))

Ascend = [84.9, 58.8, 61.7]
Descend = [78.7, 49.3, 53.0]
Random = [79.6, 35.1, 42.1]

width = 0.2
plt.figure(figsize=(6, 4))
plt.bar(x - 0.2, Ascend, width, label='Ascend', facecolor='none', hatch='///', edgecolor='#3F76B1')
plt.bar(x, Descend, width, label='Dscend', facecolor='none', hatch='|||', edgecolor='#913226')
plt.bar(x + 0.2, Random, width, label='Random', facecolor='none', hatch='---', edgecolor='#6C3483')
for i,j in zip(x-0.2, Ascend):
    plt.text(i, j, str(j), ha='center', va='bottom')
for i,j in zip(x, Descend):
    plt.text(i, j, str(j), ha='center', va='bottom')
for i,j in zip(x+0.2, Random):
    plt.text(i, j, str(j), ha='center', va='bottom')
plt.xticks(x, labels=labels)
plt.title('Analysis of Permutation Method (%)')
plt.legend()
# plt.grid(axis='y', linestyle='--')
plt.show()