import os
import platform
import psutil
import socket


def get_topology_group_prefix(path):
    """
    Extract the directory structure from a topology path (e.g. borg/800/0_1000/DE.json → borg/800/0_1000).
    This is used to group similar topologies into one experiment.
    """
    return os.path.dirname(path.replace("\\", "/").replace("topologies/", "")).strip() or "Ungrouped"


def clean_selection(selections, full_options):
    """
    Clean selection list by resolving special values.

    Resolves "[Select All]" into all valid options. Removes "[Keep original]" and any placeholder files.
    If no valid selection remains, returns None.

    Args:
        selections: The list of user-selected options.
        full_options: All available files/options.

    Returns:
        A filtered list or None.
    """

    if not selections:
        return None

    def is_valid(opt):
        return opt not in ("[Keep original]", "[Select All]") and not opt.endswith(".gitkeep")

    if "[Select All]" in selections:
        return [opt for opt in full_options if is_valid(opt)]

    filtered = [s for s in selections if is_valid(s)]
    return filtered if filtered else None


def refresh_dropdown(dropdown, folder, selected=None, keep_original=True):
    """
    Refresh a dropdown widget with updated file options from a folder.

    Rebuilds the dropdown options, optionally preserving the "[Keep original]" entry.
    Sets the current value to the selected file if present.

    Args:
        dropdown: The widget to update.
        folder: Folder to read files from.
        selected: File to set as selected (optional).
        keep_original: Whether to prepend "[Keep original]" (default True).
    """

    files = os.listdir(folder)
    options = ['[Keep original]'] + files if keep_original else files
    dropdown.options = options
    if selected in files:
        dropdown.value = selected


def get_val(lst, idx):
    return lst[idx] if idx < len(lst) else None


def parse_input(input_str):
    """
    Parse a string into a list of values, supporting ranges, lists, and combinations.

    Supports:
    - Single values: "10"
    - Comma-separated: "10,20,30"
    - Ranges with step: "1-10:2"
    - Combinations with '+': "1-5:1 + 10,15"

    Returns:
        A list of string values. Casting is handled elsewhere.
    """

    input_str = input_str.strip()
    if not input_str:
        return []

    segments = [s.strip() for s in input_str.split('+')]
    result = []

    for segment in segments:
        if '-' in segment and ':' in segment:
            start_end, step = segment.split(':')
            start, end = start_end.split('-')
            result += [str(v) for v in frange(int(start), int(end), int(step))]

        elif ',' in segment:
            result += [s.strip() for s in segment.split(',')]

        else:
            result.append(segment)

    return result


def list_files(root):
    """
    Recursively list all topology JSON files under a folder.

    Args:
        root: Root directory to search.

    Returns:
        List of file paths relative to root.
    """

    topo_files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".json"):
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                topo_files.append(rel)
    return topo_files


def frange(start, end, step):
    """
    Create a range of numeric values with a float-compatible step.

    Args:
        start: Starting value.
        end: Final value (inclusive).
        step: Step size.

    Returns:
        List of rounded float values.
    """

    result = []
    current = start
    while current <= end:
        result.append(round(current, 8))
        current += step
    return result


def safe_listdir(path):
    return os.listdir(path) if os.path.exists(path) else []


def get_system_info():
    """
    Collect basic system information for reproducibility metadata.

    Returns:
        Dictionary containing CPU, memory, and platform info.
    """

    cpu_info = {
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "memory_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
    }

    return cpu_info

def filter_files_by_keyword(files, keyword):
    keyword = keyword.strip().lower()
    return [f for f in files if keyword in f.lower()] if keyword else files