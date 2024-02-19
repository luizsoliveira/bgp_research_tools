import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

def save_3d_scatter(filename_prefix, dataset, x_column, y_column, z_column):
    #Preparing 3D scatter plots
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    #Adding regular
    ax.scatter(dataset.select_where(x_column,'LABEL',0), dataset.select_where(y_column,'LABEL',0), dataset.select_where(z_column,'LABEL',0), marker='o', label='Class 0: Regular', s=10)
    #Adding anomalous
    ax.scatter(dataset.select_where(x_column,'LABEL',1), dataset.select_where(y_column,'LABEL',1), dataset.select_where(z_column,'LABEL',1), marker='*', label='Class 1: Anomalous', s=10)

    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_zlabel(z_column)

    #Legend
    ax.legend()
    # legend = ax.legend(*[scatter1.legend_elements()[0],['a','b','c','d','e']], 
    #                 title="Legend", loc='upper left')

    # plt.show()
    filename = f"{filename_prefix}_{x_column}_{y_column}_{z_column}.png"
    plt.savefig(filename)

def save_3d_datetime_scatter(filename_prefix, dataset, y_column, z_column):
    #Preparing 3D scatter plots
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    dates_regular = dataset.select_where('DATETIME','LABEL',0)
    dates_regular = [pd.to_datetime(d) for d in dates_regular]

    dates_anomalous = dataset.select_where('DATETIME','LABEL',1)
    dates_anomalous = [pd.to_datetime(d) for d in dates_anomalous]

    # Adding regular
    ax.scatter(dates_regular, dataset.select_where(y_column,'LABEL',0), dataset.select_where(z_column,'LABEL',0), marker='o', label='Class 0: Regular')
    # Adding anomalous
    ax.scatter(dates_anomalous, dataset.select_where(y_column,'LABEL',1), dataset.select_where(z_column,'LABEL',1), marker='+', label='Class 1: Anomalous')

    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_zlabel(z_column)

    # #Legend
    # legend = ax.legend(*[scatter1.legend_elements()[0],['a','b','c','d','e']], 
    #                 title="Legend", loc='upper left')

    # plt.show()
    filename = f"{filename_prefix}_{x_column}_{y_column}_{z_column}.png"
    plt.savefig(filename)

def save_plotly_scatter(filename_prefix, dataset, x_column, y_column, z_column):
    fig = px.scatter_3d(dataset.df, x=x_column, y=y_column, z=z_column)
    filename = f"{filename_prefix}_{x_column}_{y_column}_{z_column}.png"
    fig.write_image(filename)
    # fig.show()