# ⚗️  Taipy-edit-log

This app is an experimentation on how to build an Edit Log viewer for Taipy.
It shows how to use the `edits` property of a Data Node to show a live view of all the edits on this data node.

## Installation

Taipy-core from [this branch](https://github.com/gmarabout/taipy-core/tree/gmarabout/data_node_edit_tracking) is required.

# Overview

Run the app using `python main.py`.

It provides a simple configuration with
* A simple scenario config "My_super_scenario"
* A simple pipeline with
* Two data nodes: `node_start` and `node_end`
* A simple task that just takes data from `node_start`, displays a message and returns the data as `node_end`

When started for the first time, the app shows no data:

<p align="center">
  <img src="docs/0_app_started.jpg" alt="drawing" width="700"/>
</p>

You can then create a new scenario by clicking the "Create Scenario" button:

<p align="center">
  <img src="docs/1_create_scenario.gif" alt="drawing" width="700"/>
</p>

Once created, you select the scenario from the first selector and the data node from the second selector:

<p align="center">
  <img src="docs/2_select_data_node.gif" alt="drawing" width="700"/>
</p>

When a data node is selected, the "Data Node Edit Log" section displays a live table of the edit log for this node. Notice that the node "start_node" already has an edit in its history. This is because Pickle Nodes are considered edited when they are created.

You can set a value to a node, as well as a optional comment. Notice that this operation would make sense only for Pickle data nodes...
Let's do it for the "start_node":

<p align="center">
  <img src="docs/3_set_node_value.gif" alt="drawing" width="700"/>
</p>

You can also run the scenario by clicking the "Run scenario" button:

<p align="center">
  <img src="docs/4_run_scenario.gif" alt="drawing" width="700"/>
</p>
