# Reproducibility Capsule

This capsule contains all artifacts needed to reproduce the experiments listed below using OpenDC.

## Experiments Overview

## Capsule Metadata
- **Created on**: 2025-06-29
- **OpenDC Version**: 2.4e
- **Capsule Tool Version**: 1.0.0

### Experiment 1: `carbon_experiment.json`
- **Topologies**: 4 files
<details><summary>Show Topology List</summary>

topologies/hosts277/carbon-BE_2021-2024/core16_speed2100_mem100000_carbon_topo.json
topologies/hosts277/carbon-DE_2021-2024/core16_speed2100_mem100000_carbon_topo.json
topologies/hosts277/carbon-FR_2021-2024/core16_speed2100_mem100000_carbon_topo.json
topologies/hosts277/carbon-NL_2021-2024/core16_speed2100_mem100000_carbon_topo.json
</details>

- **Workloads**: 1 files
<details><summary>Show Workload List</summary>

workload_traces/surf_month
</details>


## Execution Time per Experiment

| Experiment | Duration (seconds) |
|------------|--------------------|
| carbon_experiment.json | 76.61 |

Experiments were executed on the following system, we recommend to have at least these specifications when rerunning the experiments

## System Information

- **Machine**: AMD64
- **Processor**: Intel64 Family 6 Model 165 Stepping 2, GenuineIntel
- **Cores**: 4
- **Threads**: 8
- **Memory**: 31.84 GB
- **Platform**: Windows-10-10.0.26100-SP0
## How to Run
1. Make sure to have Java 21 and Jupyter Notebooks installed
2. Open `main.ipynb` in a Jupyter environment.
3. Click **'Run All Experiments'** to execute everything in the queue.
4. Outputs will appear in the `output/` directory.

You can also customize and build on top of the experiments provided using the same notebook and following the instructions.
