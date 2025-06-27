import os
import sys
import subprocess
import time

def run_experiment(path):
    """
    Executes a single OpenDC experiment.

    Detects platform (Windows or Linux) and invokes the appropriate runner.
    Prints output and any errors encountered.

    Args:
        path: Path to the experiment JSON file.
    """

    print("Running simulation...")

    if not os.path.exists(path):
        print(f"ERROR: Experiment file not found at {path}")
        return

    experiment_path = os.path.abspath(path)

    if sys.platform.startswith("win"):
        lib_dir = os.path.abspath("OpenDCExperimentRunner/lib")
        classpath = ";".join([
            os.path.join(lib_dir, f) for f in os.listdir(lib_dir) if f.endswith(".jar")
        ])

        java_cmd = [
            "java",
            "-classpath", classpath,
            "org.opendc.experiments.base.runner.ExperimentCli",
            "--experiment-path", experiment_path
        ]

        try:
            result = subprocess.run(java_cmd, capture_output=True, text=True)
            if result.stderr is not "":
                print("STDERR:\n", result.stderr)
        except Exception as e:
            print(f"Failed to run experiment: {e}")


    elif sys.platform.startswith("linux"):
        runner_path = "OpenDCExperimentRunner/bin/OpenDCExperimentRunner"
        if not os.path.exists(runner_path):
            print(f"ERROR: Runner not found at {runner_path}")
            return

        try:
            result = subprocess.run([runner_path, "--experiment-path", experiment_path], capture_output=True, text=True)
            if result.stderr:
                print("STDERR:\n", result.stderr)
                print("Experiment status: ")
        except Exception as e:
            print(f"Failed to run experiment: {e}")

    else:
        print("ERROR: Unsupported OS. This runner supports Windows and Linux")

def run_all_experiments(experiment_queue):

    """
    Runs all experiments in the queue sequentially and measures execution time.

    Clears the queue after execution and returns timing stats.

    Args:
        experiment_queue: List of queued experiments.

    Returns:
        A list of dictionaries with experiment names and execution durations.
    """
    
    if not experiment_queue:
        print("No experiments added")
        return
        
    print("Running all queued experiments...")
    
    experiment_times = []

    for exp in experiment_queue:
                
        filename = exp["name"]
        print(f"Running: {filename}")
        exec_path = f"experiments/{filename}"
        start_time = time.time()
        run_experiment(exec_path)
        duration = time.time() - start_time

        experiment_times.append({
            "name": filename,
            "duration_sec": round(duration, 2) if duration else None
        })


    experiment_queue.clear()
    print("All experiments completed.")
    return experiment_times