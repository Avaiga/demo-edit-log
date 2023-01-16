from taipy.gui import Gui
from taipy import Config
import taipy
from taipy.gui import notify

# ====================================================================


def task_function(data):
    """A dummy task function"""
    print(f"Executing function: {data}")
    return data


Config.configure_job_executions(mode="standalone", max_nb_of_workers=1)

node_start_cfg = Config.configure_data_node(
    id="node_start", default_data=[1, 2], description="This is the initial data node."
)
node_end_cfg = Config.configure_data_node(
    id="node_end", description="This is the result data node."
)
task_cfg = Config.configure_task(
    id="task", input=[node_start_cfg], output=node_end_cfg, function=task_function
)
pipeline_cfg = Config.configure_pipeline(id="pipeline", task_configs=[task_cfg])
Config.configure_scenario("My_super_scenario", [pipeline_cfg])

# ====================================================================
# Variables for bindings
all_scenarios = []  # List of scenarios
all_scenarios_configs = []  # List of scenario configs
all_data_nodes = []  # List of tuple[str,DataNode]

current_scenario = None
current_data_node = None
current_scenario_config = None

scenario_name = None
edits = []

value = None
commit_message = ""
create_scenario_dialog_visible = False
set_value_dialog_visible = False


# ====================================================================


def on_init(state):
    state.all_scenarios = taipy.get_scenarios()
    state.all_scenarios_configs = list(Config.scenarios.values())


def on_change(state, var_name: str, var_value):
    if var_name == "current_scenario":
        # Propagate to list of nodes:
        state.all_data_nodes = list(var_value.data_nodes.items()) if var_value else []
    if var_name == "all_data_nodes":
        # Propagate to current data node (pick any...):
        if var_value and len(var_value) > 0:
            data_node = next(iter(var_value))
            state.current_data_node = data_node
    if var_name == "current_data_node":
        # Propagate to list of edits:
        refresh_edit_log(state)


def refresh_edit_log(state):
    # Forces a refresh of the edit log:
    data_node = state.current_data_node[1]
    state.edits = get_edit_log(data_node) if data_node else []


def create_scenario_clicked(state):
    state.scenario_name = None
    state.create_scenario_dialog_visible = True


def get_edit_log(data_node):
    def _get_edit_fields(edit):
        return [str(edit.get("timestamp")), edit.get("job_id"), edit.get("message")]

    return [_get_edit_fields(edit) for edit in data_node.edits] if data_node else []


def on_submit_button_clicked(state):
    scenario = state.current_scenario
    taipy.submit(scenario)
    # Force refresh of current data node:
    refresh_edit_log(state)
    notify(state, message=f"Scenario {scenario.name} submitted!")


def on_set_value_clicked(state):
    state.set_value_dialog_visible = True


def create_scenario_dialog_action(state, id, action, payload):
    btn_idx = payload["args"][0]
    if btn_idx == 0:  # OK button
        scenario_cfg = state.current_scenario_config
        name = state.scenario_name
        scenario = taipy.create_scenario(config=scenario_cfg, name=name)
        all_scenarios = state.all_scenarios
        all_scenarios.append(scenario)
        state.all_scenarios = all_scenarios
        notify(state, message=f"Scenario {scenario.name} created!")
    state.create_scenario_dialog_visible = False


def set_value_dialog_action(state, id, action, payload):
    btn_idx = payload["args"][0]
    if btn_idx == 0:  # OK button
        data_node = state.current_data_node
        data_node[1].write(state.value, message=state.commit_message)
        state.current_data_node = data_node

    state.set_value_dialog_visible = False


history_table_columns = {
    "0": {"title": "Date"},
    "1": {"title": "Job Id"},
    "2": {"title": "Comments"},
}


scenario_manager_page = """
<|part|class_name=card|
## Data Node Selection
<|{current_scenario}|selector|lov={all_scenarios}|dropdown|label=<select a scenario>|adapter={lambda sc:sc.name}|>
<|{current_data_node}|selector|lov={all_data_nodes}|dropdown|label=<select a data node>|adapter={lambda dn:dn[0]}|>

<|Create New Scenario...|button|on_action=create_scenario_clicked|>
<|Run Scenario|button|active={current_scenario is not None}|on_action=on_submit_button_clicked|>
|>

<|part|class_name=card|
## Data Node Edit Log
<|{edits}|table|columns={history_table_columns}|width=50vw|>
<|Set value...|button|active={len(edits) > 0}|on_action=on_set_value_clicked|>
|>

<|{create_scenario_dialog_visible}|dialog|title=Create Scenario|labels=OK;Cancel|on_action=create_scenario_dialog_action|

Select a scenario config:
<|{current_scenario_config}|selector|dropdown|lov={all_scenarios_configs}|adapter={lambda cfg: cfg.id}|>

Enter a name for your scenario:

<|{scenario_name}|input|>
|>


<|{set_value_dialog_visible}|dialog|title=Set value|labels=OK;Cancel|on_action=set_value_dialog_action|
<|{value}|input|label=Enter a value|>

<|Optional commit message|expandable|expanded=False|
<|{commit_message}|input|>
|>
|>
"""


if __name__ == "__main__":
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=4)
    gui = Gui(page=scenario_manager_page)
    core = taipy.Core()
    taipy.run(core, gui, port=8080, dark_mode=False)
