from algos.algos import task_function 
from taipy import Config

Config.configure_job_executions(mode="standalone", max_nb_of_workers=1)

node_start_cfg = Config.configure_data_node(
    id="node_start", default_data=[1, 2], description="This is the initial data node."
)
node_end_cfg = Config.configure_data_node(id="node_end", description="This is the result data node.")
task_cfg = Config.configure_task(id="task", input=[node_start_cfg], output=node_end_cfg, function=task_function)
pipeline_cfg = Config.configure_pipeline(id="pipeline", task_configs=[task_cfg])
Config.configure_scenario("My_super_scenario", [pipeline_cfg])
