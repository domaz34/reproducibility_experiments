from src.utils import *
from itertools import product
import json


def update_topology_values(
    topo_template_path=None,
    topology_file=None,
    core_count_list=None, 
    core_speed_list=None, 
    memory_size_list=None,
    carbon_list=None,
    NoH_list=None,
    battery_capacity_list=None,
    starting_CI_list=None,
    charging_speed_list=None,
    expected_lifetime_list=None,
    include_battery=False,
    name=None,
    power_model_type=None,
    power_model_idle=None,
    power_model_max=None,
    power_model_power=None,
    add_power_model=False,
    generate_combinations=False
):
    """
    Generate and save new topology files based on provided variations.

    If a topology file is provided, it is used as the base template. Otherwise,
    a default one-cluster topology is generated. New topologies are created by 
    iterating over the provided lists or by generating combinations if enabled.

    - If generate_combinations is True, creates a topology for each unique combination.
    - If False, aligns values by index across lists.
    - Only non-empty inputs are used in combination generation.
    - Carbon traces and battery configs are added to clusters if provided.
    - Power model is added to hosts if enabled.

    Saves each generated topology under a structured path reflecting its parameters.
    """

    if topology_file:
        topology_path = f"{topo_template_path}{topology_file}"
        try:
            with open(topology_path, 'r') as f:
                original_topology = json.load(f)
        except Exception as e:
            print(f"Failed to load topology {topology_file}: {e}")
            return
    else:
        original_topology = {
            "clusters": [create_new_cluster(16, 2100, 100000, 1, 0)]
        }

    
    carbon_list = carbon_list or []
    NoH_list = NoH_list or []
    battery_capacity_list = battery_capacity_list or []
    starting_CI_list = starting_CI_list or []
    charging_speed_list = charging_speed_list or []
    expected_lifetime_list = expected_lifetime_list or []
    core_count_list = core_count_list or []
    core_speed_list = core_speed_list or []
    memory_size_list = memory_size_list or []

    if generate_combinations:
        inputs = {
            "carbon": carbon_list,
            "NoH": NoH_list,
            "battery_capacity": battery_capacity_list,
            "starting_CI": starting_CI_list,
            "charging_speed": charging_speed_list,
            "expected_lifetime": expected_lifetime_list,
            "core_count": core_count_list,
            "core_speed": core_speed_list,
            "memory_size": memory_size_list
        }

        active = {key: value for key, value in inputs.items() if value}

        keys, lists = zip(*active.items())

        seen = set()
        for combo in product(*lists):
            if None in combo:
                continue
            if combo in seen:
                continue
            seen.add(combo)
        
            values = dict(zip(keys, combo))

            new_topology = json.loads(json.dumps(original_topology))
            build_one_topology(
                new_topology=new_topology,
                core_count=values.get("core_count"),
                core_speed=values.get("core_speed"),
                memory_size=values.get("memory_size"),
                carbon=values.get("carbon"),
                NoH=values.get("NoH"),
                battery_capacity=values.get("battery_capacity"),
                starting_CI=values.get("starting_CI"),
                charging_speed=values.get("charging_speed"),
                expected_lifetime=values.get("expected_lifetime"),
                include_battery=include_battery,
                name=name,
                power_model_type=power_model_type,
                power_model_idle=power_model_idle,
                power_model_max=power_model_max,
                power_model_power=power_model_power,
                add_power_model=add_power_model
            )

    else:
        max_len = max(
            len(core_count_list), len(core_speed_list), len(memory_size_list),
            len(carbon_list), len(NoH_list),
            len(battery_capacity_list), len(starting_CI_list), len(charging_speed_list),
            1
        )

        for i in range(max_len):
            core_count = get_val(core_count_list, i)
            core_speed = get_val(core_speed_list, i)
            memory_size = get_val(memory_size_list, i)
            NoH = get_val(NoH_list, i)
            carbon = get_val(carbon_list, i)
            battery_capacity = get_val(battery_capacity_list, i)
            starting_CI = get_val(starting_CI_list, i)
            charging_speed = get_val(charging_speed_list, i)
            expected_lifetime = get_val(expected_lifetime_list, i)

            new_topology = json.loads(json.dumps(original_topology))
            build_one_topology(
                new_topology=new_topology,
                core_count=core_count,
                core_speed=core_speed,
                memory_size=memory_size,
                carbon=carbon,
                NoH=NoH,
                battery_capacity=battery_capacity,
                starting_CI=starting_CI,
                charging_speed=charging_speed,
                expected_lifetime=expected_lifetime,
                include_battery=include_battery,
                name=name,
                power_model_type=power_model_type,
                power_model_idle=power_model_idle,
                power_model_max=power_model_max,
                power_model_power=power_model_power,
                add_power_model=add_power_model
            )

        
def build_one_topology(new_topology,
                        core_count, core_speed, memory_size,
                        carbon, NoH,
                        battery_capacity, starting_CI, charging_speed, expected_lifetime,
                        include_battery, name,
                        power_model_type, power_model_idle,
                        power_model_max, power_model_power, add_power_model):
    
    """
    Populate and save a single topology configuration based on inputs.

    Applies cluster-level and host-level settings including carbon trace, battery,
    power model, and compute specs. Naming is handled automatically.

    """
    
    if "clusters" in new_topology:
            for cluster in new_topology["clusters"]:
                if carbon:
                    cluster["powerSource"] = {
                    "carbonTracePath": f"carbon_traces/{carbon}"
                    }
                
                if include_battery and battery_capacity is not None and starting_CI is not None and float(starting_CI) > 0:
                    cluster["battery"] = {
                        "capacity": int(battery_capacity),
                        "chargingSpeed": int(charging_speed) * int(battery_capacity) if charging_speed else 0,
                        "embodiedCarbon": 100 * int(battery_capacity),
                        "expectedLifetime": int(expected_lifetime) if int(expected_lifetime) is not None else 10
                    }

                    if "batteryPolicy" not in cluster["battery"]:
                        cluster["battery"]["batteryPolicy"] = {
                            "type": "runningMeanPlus",
                            "startingThreshold": float(starting_CI),
                            "windowSize": 168
                        }

                for host in cluster.get("hosts", []):
                    if core_count is not None:
                        host["cpu"]["coreCount"] = int(core_count)
                    if core_speed is not None: 
                        host["cpu"]["coreSpeed"] = int(core_speed)
                    if memory_size is not None:
                        host["memory"]["memorySize"] = int(memory_size)
                    if NoH is not None:
                        host["count"] = int(NoH)

                    if add_power_model:
                        if power_model_type is not None:
                            power_model = {"modelType": power_model_type}

                            if power_model_power is not None:
                                power_model["power"] = float(power_model_power)
                            if power_model_idle is not None:
                                power_model["idlePower"] = float(power_model_idle)
                            if power_model_max:
                                power_model["maxPower"] = float(power_model_max)
                            
                            host["powerModel"] = power_model

        
    path = build_topology_path(carbon = carbon,
                                    NoH = NoH,
                                    battery_capacity = battery_capacity,
                                    charging_speed=charging_speed,
                                    include_battery = include_battery,
                                    core_count = core_count,
                                    core_speed = core_speed,
                                    memory_size = memory_size,
                                    name = name
                                )
                                                

    save_topology(new_topology, path)
  
        

def build_topology_path(
    carbon,
    NoH,
    battery_capacity,
    charging_speed,
    include_battery,
    core_count,
    core_speed,
    memory_size,
    name
):
    
    """
    Construct a relative file path for a generated topology file.

    Path is built using the most relevant features (e.g. NoH, battery, carbon, CPU settings).
    File name is composed using name and other hardware specs.
    Feel free to adjust to your taste.

    Returns:
        Relative file path to use when saving the topology.
    """

    # Folder structure
    path_parts = []
    if NoH is not None:
        path_parts.append(f"hosts{NoH}")
    if include_battery and battery_capacity is not None and charging_speed is not None:
        path_parts.append(f"bat{battery_capacity}_{charging_speed}")
    if carbon:
        path_parts.append(f"carbon-{os.path.splitext(carbon)[0]}")
    
    
    # Filename
    feature_bits = []
    if core_count is not None:
        feature_bits.append(f"core{core_count}")
    if core_speed is not None:
        feature_bits.append(f"speed{core_speed}")
    if memory_size is not None:
        feature_bits.append(f"mem{memory_size}")

    
    if name:
        default_name = f"{name}.json"
    else:
        default_name = "topology.json"
    fname = "_".join(feature_bits) + f"_{default_name}" if feature_bits else default_name

    return "/".join(path_parts + [fname])



def create_new_cluster(core_count, core_speed, memory_size, host_count, index): 
    """
    Create a default cluster with a single host entry.

    Returns:
        A cluster dictionary structure to be included in the topology.
    """

    return {
        "name": f"C{index}",
        "hosts": [
            {
                "name": f"H{index}", 
                "cpu": {
                    "coreCount": core_count,
                    "coreSpeed": core_speed,
                },
                "memory": {
                    "memorySize": memory_size,
                },
                "count": host_count
            }
        ]
    }


def save_topology(topology: dict, rel_path: str):

    """
    Save a topology dictionary to disk under the topologies/ directory.

    Creates subfolders as necessary.
    """
    
    full_path = f"topologies/{rel_path}"
    os.makedirs(os.path.dirname(full_path), exist_ok=True)  
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(topology, f, indent=4)
    print(f"Generated {rel_path}")