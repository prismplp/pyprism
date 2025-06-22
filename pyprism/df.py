from pyprism.parser import read_sw_data
import sklearn
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import KBinsDiscretizer
import pandas as pd


def sw2df(filename):
    data, m = read_sw_data(filename, use_array=True)
    h1 = ["Name", "Arity", "Term", "Status", "Vals", "Param"]
    h2 = ["Arg" + str(i + 1) for i in range(m)]
    data_ = [line + args + [""] * (m - len(args)) for line, args in data]
    return pd.DataFrame(data_, columns=h1 + h2)


# Function to extract conditional probability distribution from a DataFrame
def get_conditional_dist(df_, arg_cond="Arg2"):
    data = []  # List to hold the probability values
    name_list_cond = []  # List of condition labels (for y-axis)
    name_list_val = None  # List of value labels (for x-axis)
    for i, r in df_.iterrows():
        name_list_cond.append(r[arg_cond])
        n = len(r["Vals"])
        arr = [0] * n
        name_list_val = [""] * n
        # Sort value-param pairs and populate the probability and value names
        for i, (v, p) in enumerate(sorted(zip(r["Vals"], r["Param"]))):
            arr[i] = p  # print(i,v,p)
            name_list_val[i] = str(v)
        data.append(arr)
    prob = np.array(data)
    return prob, name_list_cond, name_list_val


def rename_axis(c, attr_cond, org_name_list):
    out_list = []
    if attr_cond is None:
        return org_name_list
    if isinstance(attr_cond, dict):
        if c in attr_cond:
            l = attr_cond[c]
        else:
            return org_name_list
    else:
        l = attr_cond
    for e in org_name_list:
        i = int(e)
        if i < len(l):
            out_list.append(l[i])
        else:
            out_list.append(e)
    return out_list


# Function to iterate over one condition (arg_var),
# compute conditional distribution for another (arg_cond), and plot
def get_conditional_dist2(
    df,
    arg_var="Arg1",
    arg_cond="Arg2",
    attr_var=None,
    attr_cond=None,
    attr_val=None,
    cond_var_name="",
):
    cond_list = df[arg_var].unique()
    # Process each condition
    for c in cond_list:
        df_ = df[df[arg_var] == c].sort_values(arg_cond)
        prob, name_list_cond, name_list_val = get_conditional_dist(df_, arg_cond)
        if attr_var is not None:
            c = attr_var[int(c)]
        # Optionally map condition labels using provided list
        name_list_cond = rename_axis(c, attr_cond, name_list_cond)
        name_list_val = rename_axis(c, attr_val, name_list_val)
        # Plot the computed conditional distribution
        if cond_var_name != "":
            title = "P({} = value | {} = condition)".format(c, cond_var_name)
        else:
            title = "P({} = value | condition)".format(c)
        plot_conditional_dist(prob, name_list_cond, name_list_val, title=title)


# Function to visualize a conditional probability matrix as a heatmap
def plot_conditional_dist(prob, name_list_cond, name_list_val, title=""):
    plt.imshow(prob)
    plt.xticks(range(len(name_list_val)), name_list_val)
    plt.xlabel("value")
    plt.yticks(range(len(name_list_cond)), name_list_cond)
    plt.ylabel("condition")
    plt.xticks(rotation=45)
    plt.title(title)
    plt.colorbar()
    plt.show()


def disc2binlist(disc):
    bin = disc.bin_edges_[0]
    return ["{:0.1f}-{:0.1f}".format(e1, e2) for e1, e2 in zip(bin[:-1], bin[1:])]


def _get_group_label(idx, group_key, group_mapping):
    if group_key is not None:
        label = list(df_[group_key])[idx]
        if group_mapping is not None and isinstance(group_mapping, list):
            label = group_mapping[int(label)]
        elif group_mapping is not None:
            label = group_mapping[label]
    elif group_mapping is not None:
        label = group_mapping[idx]
    else:
        label = f"Group {idx+1}"
    return label


def plot_dist(df_, attr_val=None, group_key=None, group_mapping=None, title=""):
    # Bar width per group
    num_groups = len(df_)
    width = 0.8 / num_groups
    # Plots for each group
    x_labels = None
    for idx in range(num_groups):
        v = list(df_["Vals"])[idx]
        x_labels = rename_axis(None, attr_val, v)
        x = np.arange(len(x_labels))
        param = list(df_["Param"])[idx]
        label = _get_group_label(idx, group_key, group_mapping)
        plt.bar(x + idx * width, param, width=width, label=label)
    plt.xticks(x + width * (num_groups - 1) / 2, x_labels, rotation=90)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
