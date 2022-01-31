import numpy as np
import h5py
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table
import os

default_path = "stats.h5"
pattern_dict = {"projection": ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "4D_SCAN", "SINOMOVIE"],
                "reconstruction": ["VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D"]}
_key_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]

def load_file(file_name=default_path):
    return h5py.File(file_name, 'r')


def get_dicts(file):
    stats_dict = {}
    index_dict = {}
    stats_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [], "RMSD": []}
    stats_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                    "RMSD": []}
    index_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [], "RMSD": []}
    index_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [],
                                    "RMSD": []}

    group = file["stats"]
    for space in ("projection", "reconstruction"):
        for index, stat in enumerate(["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]):
            for key in list(group.keys()):
                if group[key].attrs.get("pattern") in pattern_dict[space]:
                    index_dict[space][stat].append(f"{key}: {group[key].attrs.get('plugin_name')}")
                    if group[key].ndim == 1:
                        if len(group[key]) > index:
                            stats_dict[space][stat].append(group[key][index])
                        else:
                            stats_dict[space][stat].append(None)
                    elif group[key].ndim == 2:
                        if len(group[key][0]) > index:
                            stats_dict[space][stat].append(group[key][:, index])
                        else:
                            stats_dict[space][stat].append(None)
    return stats_dict, index_dict


def remove_arrays(stats_dict):
    for space in list(stats_dict.keys()):
        for stat in list(stats_dict[space].keys()):
            for index, value in enumerate(stats_dict[space][stat]):
                if isinstance(value, np.ndarray):
                    stats_dict[space][stat][index] = stats_dict[space][stat][index][0]
    return stats_dict


def generate_stats(filepath=default_path):
    f = load_file(filepath)
    stats_dict, index_dict = get_dicts(f)
    p_stats = pd.DataFrame(stats_dict["projection"], index_dict["projection"]["max"])
    r_stats = pd.DataFrame(stats_dict["reconstruction"], index_dict["reconstruction"]["max"])
    all_stats = pd.concat([p_stats, r_stats], keys=["Projection", "Reconstruction"])

    stats_dict = remove_arrays(stats_dict)

    p_stats = pd.DataFrame(stats_dict["projection"], index_dict["projection"]["max"])
    r_stats = pd.DataFrame(stats_dict["reconstruction"], index_dict["reconstruction"]["max"])

    kwds = {"marker": "x"}

    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.plot(p_stats, "x-")
    ax2.plot(r_stats, "x-")
    ax1.set_title("Projection Stats")
    ax2.set_title("Reconstruction Stats")
    fig.autofmt_xdate()
    for ax in (ax1, ax2):
        ax.grid(True)
    ax2.legend(_key_list, loc="right", bbox_to_anchor=(1.8, 0.5))

    plt.plot(grid=True, title="Projection Space Stats", **kwds)
#    r_stats.plot(ax=grid=True, title="Reconstruction Space Stats", **kwds)
    #plt.legend(loc="right", bbox_to_anchor=(1.35, 0.5))
    plt.savefig("stats.png", bbox_inches="tight")
    #r_stats.plot(grid=True, title="Reconstruction Space Stats", **kwds)
    #plt.legend(loc="right", bbox_to_anchor=(1.35, 0.5))
    #plt.savefig("reconstruction_stats.png", bbox_inches="tight")

    all_stats.to_html("stats_table.html")

    #all_stats = all_stats.reset_index()

    #ax = plt.subplot(111, frame_on=False)
    #ax.xaxis.set_visible(False)  # hide the x axis
    #ax.yaxis.set_visible(False)  # hide the y axis
    #t = table(ax, all_stats, loc="center")
    #plt.savefig("stats_table.png")
    #excel_data = pd.ExcelWriter("stats_table.xlsx")
    #all_stats.to_excel(excel_data)
    #excel_data.save()

generate_stats()