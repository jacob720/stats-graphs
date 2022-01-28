import numpy as np
import h5py
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import os


print(matplotlib.pyplot.get_backend())
default_path = "stats.h5"
stat_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]
pattern_dict = {"projection": ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "4D_SCAN", "SINOMOVIE"],
                "reconstruction": ["VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D"]}


def load_file(file_name=default_path):
    return h5py.File(file_name, 'r')

def get_dicts(file):
    stats_dict = {"Ppojection": {}, "reconstruction": {}}
    index_dict = {"projection": {}, "reconstruction": {}}
    stats_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [], "RMSD": []}
    stats_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [], "RMSD": []}
    index_dict["projection"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [], "RMSD": []}
    index_dict["reconstruction"] = {"max": [], "min": [], "mean": [], "mean_std_dev": [], "median_std_dev": [], "RMSD": []}

    group = file["stats"]
    for space in ("projection", "reconstruction"):
        for index, stat in enumerate(["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]):
            for key in list(group.keys()):
                if group[key].attrs.get("pattern") in pattern_dict[space]:
                    index_dict[space][stat].append(f"{key} ({group[key].attrs.get('plugin_name')})")
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

f = load_file()
stats_dict, index_dict = get_dicts(f)
p_stats = pd.DataFrame(stats_dict["projection"], index_dict["projection"]["max"])
r_stats = pd.DataFrame(stats_dict["reconstruction"], index_dict["reconstruction"]["max"])
all_stats = pd.concat([p_stats, r_stats], keys=["Projection", "Reconstruction"])
p_stats.plot(x="max", y="min")
#all_stats["max"] = all_stats["max"].astype(float)
#all_stats["min"] = all_stats["min"].astype(float)
a = input("Waiting")
#all_stats.plot(x="max", y="min")