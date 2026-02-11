"""
Module reads an events file and network file, constructs approach df,
and saves it to a file.
"""

import matsim
import pandas as pd


# Filepaths.
network_filepath = "matsim/example_network.xml.gz"
event_filepath = "matsim/example_events.xml.gz"
output_filepath = "outputs/"

# Read network file and initialize a dataframe containing every link
# to link connection.

net = matsim.read_network(network_filepath)
print("Network read.")

# Intialize approach dataframe. each row is a link id with a possible
# connected link and the volume of this connection. All volumes start
# at zero.

links = net.links[["link_id", "from_node", "to_node"]]

approach_df = links.merge(
    links, left_on="to_node", right_on="from_node", suffixes=("_from", "_to")
)[["link_id_from", "link_id_to"]].rename(
    columns={"link_id_from": "link_id", "link_id_to": "to_link"}
)
approach_df["volume"] = 0

print("Approach construction complete.")

# Read events file into event object, only keeping entered and left link
# events.

event_types = ["entered link", "left link"]
events = matsim.event_reader(event_filepath, event_types)
data_list = []
for event in events:
    data_list.append(event)
event_df = pd.DataFrame.from_records(data_list)
print("Event dataframe created.")

# Iterate over every user and update the volume corresponding to their
# trip.

# Sort by time and identify transition locations.
event_df = event_df.sort_values(["vehicle", "time"])

event_df["next_type"] = event_df.groupby("vehicle")["type"].shift(-1)
event_df["next_link"] = event_df.groupby("vehicle")["link"].shift(-1)
transitions = event_df[
    (event_df["type"] == "left link")
    & (event_df["next_type"] == "entered link")
].copy()
transitions["link_id"] = transitions["link"].astype(str)
transitions["to_link"] = transitions["next_link"].astype(str)

# Count number of transitions between each link.
counts = (
    transitions.groupby(["link_id", "to_link"])
    .size()
    .reset_index(name="count")
)
# Append to approach df.
approach_df = approach_df.merge(counts, on=["link_id", "to_link"], how="left")
approach_df["volume"] += approach_df["count"].fillna(0).astype(int)
approach_df.drop(columns="count", inplace=True)

# Save files.
approach_output = output_filepath + "approach_vol.csv"
approach_df.to_csv(approach_output, index=False)
print(f"Approach dataframe saved to {approach_output}")

network_dict_output = output_filepath + "link_node_dict.csv"
net.links[["link_id", "from_node", "to_node"]].to_csv(
    network_dict_output, index=False
)
print(f"Network dictionary saved to {network_dict_output}")
