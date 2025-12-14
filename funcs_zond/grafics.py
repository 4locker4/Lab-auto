import matplotlib.pyplot as plt

#Common parameters to all graphs
plt.rcParams['axes.labelsize'] = 25
plt.rcParams['xtick.labelsize'] = 25
plt.rcParams['ytick.labelsize'] = 25
plt.rcParams['axes.grid'] = True

#Параметры графиков, которые отвечают за точки на графике
scatter_params ={
    "alpha" : .4,
    "s" : 70,
    "ls" : 'None'
}
#Параметры графиков, которые отвечают за кресты ошибок
error_bar_params = {
    "ecolor" : 'black',
    "ls" : 'None',
    "elinewidth" : 0.5,
    "capsize" : 2,
    "markeredgewidth" : 0.5
}
#Параметры графиков, которые строют аппроксимацию
aprox_params = {
    "color" : 'black',
    "lw" : 1,
    "alpha" : 0.8
}
#
frame_params = {
    "color": "black",
    "alpha": 0.4,
    "ls": 'dashed'
}