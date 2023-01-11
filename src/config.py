from taipy.core import Config, Scope
from algorithms import *


# Data Node Configs

# Input Datanode configuration
init_data_config = Config.configure_csv_data_node(
    id="diamond_data",
    path="Data/diamonds.csv",
    has_header=True,
    scope=Scope.GLOBAL,
    cacheable=True,
)
# Datanode with categories encoded
adjusted_data_config = Config.configure_data_node(
    id="adjusted_data", scope=Scope.GLOBAL, cacheable=True
)

# Data Node holding names of columns to drop
drop_cols_cfg = Config.configure_data_node(
    id="drop_cols", scope=Scope.SCENARIO, default_data=["cut"]
)

# Datanode with split of train and test datasets
split_data_config = Config.configure_data_node(
    id="split_data", scope=Scope.GLOBAL, cacheable=True
)
final_data_config = Config.configure_data_node(
    id="final_data", scope=Scope.SCENARIO, cacheable=True
)

# XGB Model Datanode
xgb_model_config = Config.configure_data_node(id="xgb_model", scope=Scope.SCENARIO)

# XGB predictions Datanode

xgb_pred_config = Config.configure_data_node(id="xgb_pred", scope=Scope.SCENARIO)


# Random Forest Model Datanode
rf_model_config = Config.configure_data_node(id="rf_model", scope=Scope.SCENARIO)

# Random Forest predictions Datanode
rf_pred_config = Config.configure_data_node(id="rf_pred", scope=Scope.SCENARIO)

# Output Data
output_data_config = Config.configure_data_node(id="output_data", scope=Scope.SCENARIO)


# Task Configs

# Create Categories
adjust_data_task_config = Config.configure_task(
    id="adjust_data",
    input=final_data_config,
    output=adjusted_data_config,
    function=create_categories,
)


# Drop Columns task config
drop_cols_task_config = Config.configure_task(
    id="drop_cols_task",
    input=[adjusted_data_config, drop_cols_cfg],
    output=final_data_config,
    function=drop_cols,
)


# Encode Categories
adjust_data_task_config = Config.configure_task(
    id="adjust_data",
    input=init_data_config,
    output=adjusted_data_config,
    function=create_categories,
)

# Split Data task config
split_data_task_config = Config.configure_task(
    id="split_data_task",
    input=final_data_config,
    output=split_data_config,
    function=split_data,
)
# Train XGB Model Task Config
train_xgb_config = Config.configure_task(
    id="fit_xgb_task",
    input=split_data_config,
    output=xgb_model_config,
    function=train_xgb,
)
# Train Random Forest Task Config
train_rf_config = Config.configure_task(
    id="fit_rf_task", input=split_data_config, output=rf_model_config, function=train_rf
)

# Predict XGB Task Config
predict_xgb_config = Config.configure_task(
    id="pred_xgb_task",
    input=[xgb_model_config, split_data_config],
    output=xgb_pred_config,
    function=predict_m,
)

# Predict Random Forest Task Config
predict_rf_config = Config.configure_task(
    id="pred_rf_task",
    input=[rf_model_config, split_data_config],
    output=rf_pred_config,
    function=predict_m,
)

# Create Output Data Frame Task config
output_config = Config.configure_task(
    id="output_task",
    input=[split_data_config, xgb_pred_config, rf_pred_config],
    output=output_data_config,
    function=create_output_data,
)

# Pipeline Configuration
baseline_pipeline_cfg = Config.configure_pipeline(
    "main_pipeline",
    task_configs=[
        adjust_data_task_config,
        drop_cols_task_config,
        split_data_task_config,
        train_xgb_config,
        predict_xgb_config,
        train_rf_config,
        predict_rf_config,
        output_config,
    ],
)
# Scenario configuration
scenario_cfg = Config.configure_scenario(
    id="scenario", pipeline_configs=[baseline_pipeline_cfg]
)
