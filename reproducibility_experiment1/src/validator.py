import os
import json
import pandas as pd


def validate_experiments(experiment_queue):
    """
    Checks whether topologies, workloads, and failure models exist in each experiment file.

    Loops over all experiments in the queue and verifies that all referenced files exist.
    Can be extended for more robust validation in the future.

    Args:
        experiment_queue: List of experiment metadata dicts with 'name' field.

    Returns:
        True if all files are valid and exist, False otherwise.
    """

    for exp in experiment_queue:
        name = exp["name"]
        exp_path = f"experiments/{name}"

        try:
            with open(exp_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read '{name}': {e}")
            continue

        try:
            check_files("topologies", data, name)
            check_files("workloads", data, name)
            check_files("failureModels", data, name)
        except Exception as e:
            print(f"Validation failed for '{name}': {e}")
            return False
    
    print(f"Validation Passed")
    return True


def check_files(json_key, data, name):
    """
    Helper function that checks whether a file exists at the path specified in a given key.

    Args:
        json_key: Key in the experiment file to inspect (e.g., 'topologies').
        data: Parsed JSON contents of the experiment file.
        name: Name of the experiment (used for error messages).

    Raises:
        ValueError: If an entry under the key is missing 'pathToFile'.
        FileNotFoundError: If the file path specified doesn't exist.
    """

    if json_key not in data:
        return 
    for entry in data[json_key]:
        file_path = entry.get("pathToFile")
        if not file_path:
            raise ValueError(f"Missing 'pathToFile' in {json_key} entry of '{name}': {entry}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found for {json_key} in '{name}': {file_path}")


def get_parquet_files_recursive(root_dir):
    """
    Recursively traverses a directory and collects all .parquet files.

    Args:
        root_dir: Directory to scan.

    Returns:
        Dictionary mapping relative paths to absolute file paths.
    """

    parquet_files = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".parquet"):
                relative_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                parquet_files[relative_path] = os.path.join(dirpath, filename)
    return parquet_files


def compare_experiment_outputs(orig_path, repr_path):
    """
    Compares whether the experiment output files from two directories match.

    Checks for file presence and compares data content using Pandas.

    Args:
        orig_path: Path to original experiment output folder.
        repr_path: Path to reproduced experiment output folder.

    Returns:
        True if files exist and dataframes match, False otherwise.
    """

    try:
        orig_files = get_parquet_files_recursive(orig_path)
        repr_files = get_parquet_files_recursive(repr_path)

        missing = set(orig_files.keys()) - set(repr_files.keys())
        extra = set(repr_files.keys()) - set(orig_files.keys())
        if missing or extra:
            return False

        for rel_path in orig_files:
            df1 = pd.read_parquet(orig_files[rel_path])
            df2 = pd.read_parquet(repr_files[rel_path])
            if not df1.equals(df2):
                return False
        return True
    except Exception as e:
        return False


def compare_all_experiments_outputs():
    pairs = []

    for parent, dirs, _ in os.walk("output"):
        for d in dirs:
            if d.startswith("repr_"):
                repr_dir = os.path.join(parent, d)
                orig_dir = os.path.join(parent, d[len("repr_"):])

                if os.path.isdir(orig_dir):
                    if not get_parquet_files_recursive(orig_dir) and not get_parquet_files_recursive(repr_dir):
                        continue
                    pairs.append((orig_dir, repr_dir))

    if not pairs:
        print("No experiment pairs found.")
        return

    all_ok = True
    for orig_path, repr_path in pairs:
        rel = os.path.relpath(orig_path, "output")
        if not compare_experiment_outputs(orig_path, repr_path):
            all_ok = False

    if all_ok:
        print("All experiments match successfully.")
    else:
        print("Some experiments did NOT match.")