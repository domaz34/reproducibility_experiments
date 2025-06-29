
import os
import json
import datetime as dt


def generate_metadata_section():
    """
    Returns a list of lines containing capsule metadata.

    This includes generation date, OpenDC version, and tool version.
    Update this if OpenDC or capsule format changes.
    """

    return [
        "## Capsule Metadata",
        f"- **Created on**: {dt.datetime.now().strftime('%Y-%m-%d')}",
        "- **OpenDC Version**: 2.4e",
        "- **Capsule Tool Version**: 1.0.0",
        ""
    ]

def generate_readme_from_queue(experiment_queue, stats, output_path="README.md", experiments_dir="experiments"):
    """
    Generates a README.md file summarizing the experiments and system context.

    Args:
        experiment_queue: List of experiment dicts, each with a `name` key.
        stats: Dictionary with experiment durations and system info.
        output_path: Path where the README should be saved.
        experiments_dir: Directory where experiment JSON files are located.

    Returns:
        Path to the generated README file.
    """

    readme_lines = [
        "# Reproducibility Capsule",
        "",
        "This capsule contains all artifacts needed to reproduce the experiments listed below using OpenDC.",
        "",
        "## Experiments Overview",
        ""
    ]

    readme_lines += generate_metadata_section()

    for i, exp in enumerate(experiment_queue, start=1):
        name = exp["name"]
        readme_lines.append(f"### Experiment {i}: `{name}`")

        exp_path = f"{experiments_dir}/{name}"
        try:
            with open(exp_path) as f:
                data = json.load(f)
        except Exception:
            readme_lines.append("")
            continue

        topologies = [t["pathToFile"] for t in data.get("topologies", [])]
        workloads = [w["pathToFile"] for w in data.get("workloads", [])]
        failures = [f["pathToFile"] for f in data.get("failureModels", [])]

        if topologies:
            readme_lines.append(f"- **Topologies**: {len(topologies)} files")
            readme_lines.append("<details><summary>Show Topology List</summary>\n")
            readme_lines += [f"{t}" for t in topologies]
            readme_lines.append("</details>\n")

        if workloads:
            readme_lines.append(f"- **Workloads**: {len(workloads)} files")
            readme_lines.append("<details><summary>Show Workload List</summary>\n")
            readme_lines += [f"{w}" for w in workloads]
            readme_lines.append("</details>\n")

        if failures:
            readme_lines.append(f"- **Failures**: {len(failures)} files")
            readme_lines.append("<details><summary>Show Failure List</summary>\n")
            readme_lines += [f"{f}" for f in failures]
            readme_lines.append("</details>\n")

        readme_lines.append("")



    readme_lines += [
        "## Execution Time per Experiment",
        "",
        "| Experiment | Duration (seconds) |",
        "|------------|--------------------|"
    ]
    for exp_stat in stats.get("experiments", []):
        name = exp_stat.get("name", "unknown")
        duration = exp_stat.get("duration_sec", "N/A")
        readme_lines.append(f"| {name} | {duration} |")


    sysinfo = stats.get("system_info", {})
    readme_lines += [
        "",
        "Experiments were executed on the following system, we recommend to have at least these specifications when rerunning the experiments",
        "",
        "## System Information",
        "",
        f"- **Machine**: {sysinfo.get('machine', 'N/A')}",
        f"- **Processor**: {sysinfo.get('processor', 'N/A')}",
        f"- **Cores**: {sysinfo.get('cores', 'N/A')}",
        f"- **Threads**: {sysinfo.get('threads', 'N/A')}",
        f"- **Memory**: {sysinfo.get('memory_gb', 'N/A')} GB",
        f"- **Platform**: {sysinfo.get('platform', 'N/A')}",
    ]

    readme_lines += [
        "## How to Run",
        "1. Make sure to have Java 21 and Jupyter Notebooks installed",
        "2. Open `main.ipynb` in a Jupyter environment.",
        "3. Click **'Run All Experiments'** to execute everything in the queue.",
        "4. Outputs will appear in the `output/` directory.",
        "",
        "You can also customize and build on top of the experiments provided using the same notebook and following the instructions.",
        ""
    ]

    try:
        with open(output_path, "w") as f:
            f.write("\n".join(readme_lines))
        print(f"README generated at {output_path}")
    except Exception as e:
        print(f"Failed to generate README: {e}")

    return output_path
