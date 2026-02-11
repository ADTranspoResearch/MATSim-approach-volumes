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
approach_list = []

total_length = net.links.shape[0]
i=0
threshold=0.1
for _, from_link in net.links.iterrows():
    to_links = net.links.loc[net.links["from_node"] == from_link["to_node"]]
    for _, to_link in to_links.iterrows():
        approach_list.append(
            {
                "link_id": str(from_link["link_id"]),
                "to_link": str(to_link["link_id"]),
                "volume": 0,
            }
        )
    i+=1
    pct_complete = i/total_length
    if pct_complete > threshold:
        print(f"Approach construction {int(round(threshold,2)*100)}% complete.")
        threshold += 0.1
approach_df = pd.DataFrame.from_records(approach_list)
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

agents = event_df["vehicle"].unique()
total_length = agents.shape[0]
i=0
threshold = 0.1
for agent in agents:
    agent_event_df = event_df.loc[event_df["vehicle"] == agent]
    last_event = "entered link"
    from_link_id = None
    to_link_id = None
    for _, event in agent_event_df.iterrows():
        event_type = event["type"]
        if event_type == last_event:
            continue
        else:
            if event_type == "left link":
                from_link_id = str(event["link"])
            elif event_type == "entered link":
                to_link_id = str(event["link"])
                approach_df.loc[
                    (approach_df["link_id"] == from_link_id)
                    & (approach_df["to_link"] == to_link_id),
                    "volume",
                ] += 1
            last_event = event_type
    i+=1
    pct_complete = i/total_length
    if pct_complete > threshold:
        print(f"events process {int(round(threshold,2)*100)}% complete.")
        threshold += 0.1

approach_output = output_filepath + "approach_vol.csv"
approach_df.to_csv(approach_output, index=False)
print(f"Approach dataframe saved to {approach_output}")

network_dict_output = output_filepath + "link_node_dict.csv"
net.links[["link_id", "from_node", "to_node"]].to_csv(
    network_dict_output, index=False
)
print(f"Network dictionary saved to {network_dict_output}")