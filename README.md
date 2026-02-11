# MATSim-approach-volumes
Module to calculate the traffic volumes of each approach at a node.

Takes the events file and network file from a MATSim simulation and
creates a data table containing volumes for each approach in the network.
Outputs an approach volume data table and a link-node dictionary table.

# How to use.
- Add your event file and network file into the "matsim" folder.
- Update the filename variables in "main.py"
- Run the code
- Resulting files will be saved in "outputs" folder

requirements:
- Python 3.x
- Pandas library
- matsim-tools library