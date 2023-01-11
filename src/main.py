from taipy.gui import Gui
from taipy import Config
import taipy
from taipy.gui import notify


def task_function(data):
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
pipeline_cfg = Config.configure_pipeline(
    id="pipeline", task_configs=[task_cfg])
Config.configure_scenario("My_super_scenario", [pipeline_cfg])


def create_scenario(state, scenario_name, scenario_cfg):
    scenario = taipy.create_scenario(scenario_cfg, name=scenario_name)
    state.all_scenarios += [(scenario.id, scenario_name)]


def create_scenario_clicked(state):
    state.scenario_name = None
    state.create_scenario_dialog_visible = True


all_scenarios = []
all_scenarios_configs = []
current_scenario = None
current_task = None
current_data_node = None
current_scenario_config_id = None
create_scenario_dialog_visible = False
set_value_dialog_visible = False
scenario_name = None
edits = []
all_data_nodes = []
value = None
commit_message = ""


def on_init(state):
    state.all_scenarios = [(scenario.id, scenario.name)
                           for scenario in taipy.get_scenarios()]
    state.all_scenarios_configs = [
        scenario_cfg.id for scenario_cfg in Config.scenarios.values()]


def get_edit_history(data_node):
    def _get_edit_fields(edit):
        return [str(edit.get("timestamp")), edit.get("job_id"), edit.get("message")]

    return [
        _get_edit_fields(edit) for edit in data_node.edits
    ]


def get_all_data_nodes(scenario_id):
    scenario = taipy.get(scenario_id)
    return [
        data_node_name for data_node_name in scenario.data_nodes.keys()
    ]


def current_scenario_selected(state):
    scenario_id = state.current_scenario[0]
    state.all_data_nodes = get_all_data_nodes(scenario_id)


def current_data_node_selected(state):
    data_node_name = state.current_data_node
    scenario_id = state.current_scenario[0]
    scenario = taipy.get(scenario_id)
    selected_data_node = scenario.data_nodes[data_node_name]
    state.edits = get_edit_history(selected_data_node)


def on_submit_button_clicked(state):
    scenario_id = state.current_scenario[0]
    scenario = taipy.get(scenario_id)
    if not scenario:
        raise (f"Could not retrieve Scenario ID {scenario_id}")
    taipy.submit(scenario)
    notify(state, message=f"Scenario {scenario.name} submitted!")

    # Refresh the edit log of the current data node:
    data_node_name = state.current_data_node
    selected_data_node = scenario.data_nodes[data_node_name]
    state.edits = get_edit_history(selected_data_node)


def on_set_value_clicked(state):
    state.set_value_dialog_visible = True


def create_scenario_dialog_action(state, id, action, payload):
    btn_idx = payload["args"][0]
    if btn_idx == 0:  # OK button
        id = state.current_scenario_config_id
        name = state.scenario_name
        selection = [
            scenario_cfg
            for scenario_cfg in Config.scenarios.values()
            if scenario_cfg.id == id
        ]
        if len(selection) == 0:
            raise ("No config found for ID: " + id)
        scenario_cfg = selection[0]
        scenario = create_scenario(state, name, scenario_cfg)
        state.current_scenario = scenario

    state.create_scenario_dialog_visible = False
    notify(state, message=f"Scenario {name} created!")


def set_value_dialog_action(state, id, action, payload):
    btn_idx = payload["args"][0]
    if btn_idx == 0:  # OK button
        data_node_name = state.current_data_node
        scenario_id = state.current_scenario[0]
        scenario = taipy.get(scenario_id)
        data_node = scenario.data_nodes[data_node_name]
        data_node.write(state.value, message=state.commit_message)
        # Refresh edit log:
        state.edits = get_edit_history(data_node)

    state.set_value_dialog_visible = False


history_table_columns = {
    "0": {"title": "Date"},
    "1": {"title": "Job Id"},
    "2": {"title": "Comments"}
}


scenario_manager_page = """
<|part|class_name=card|
## Data Node Selection
<|{current_scenario}|selector|lov={all_scenarios}|dropdown|label=<select a scenario>|on_change=current_scenario_selected|>
<|{current_data_node}|selector|lov={all_data_nodes}|dropdown|label=<select a data node>|on_change=current_data_node_selected|>

<|Create New Scenario...|button|on_action=create_scenario_clicked|>
|>

<|part|class_name=card|
## Data Node Edit Log
<|{edits}|table|columns={history_table_columns}|width=50vw|>
<|Run Scenario|button|on_action=on_submit_button_clicked|>
<|Set value...|button|active={len(edits) > 0}|on_action=on_set_value_clicked|>
|>

<|{create_scenario_dialog_visible}|dialog|title=Create Scenario|labels=OK;Cancel|on_action=create_scenario_dialog_action|

Select a scenario config:
<|{current_scenario_config_id}|selector|dropdown|lov={all_scenarios_configs}|>

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
    Config.configure_job_executions(mode="standalone", nb_of_workers=4)
    gui = Gui(page=scenario_manager_page)
    core = taipy.Core()
    taipy.run(core, gui, port=8080, dark_mode=False)
