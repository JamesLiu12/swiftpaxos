import sys
import yaml
from .config_loader import ConfigLoader
from evaluate.node import Node
import os

def change_conflict(conflict_value):
    """
    Update conflict settings in local.conf and evaluate/config.yaml
    
    Args:
        c: Conflict value
    """    
    ConfigLoader()
    working_dir = os.path.expanduser(Node.working_dir)
    local_conf_path = os.path.join(working_dir, 'local.conf')
    config_yaml_path = os.path.join(working_dir, 'evaluate', 'config.yaml')

    try:
        with open(local_conf_path, 'r') as f:
            lines = f.readlines()
        
        # Find and replace the line starting with 'conflicts:'
        for i, line in enumerate(lines):
            if line.strip().startswith('conflicts:'):
                lines[i] = f'conflicts:   {conflict_value}\n'
                break
        
        # Write back to local.conf
        with open(local_conf_path, 'w') as f:
            f.writelines(lines)
        
        print(f"Updated local.conf - conflicts: {conflict_value}")
        
    except FileNotFoundError:
        print(f"Error: {local_conf_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating local.conf: {e}")
        sys.exit(1)
    
    # Update evaluate/config.yaml
    try:
        with open(config_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update test_name
        config['test_name'] = f'conflict-{conflict_value}'
        
        # Write back to evaluate/config.yaml
        with open(config_yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Updated evaluate/config.yaml - test_name: conflict-{conflict_value}")
        
    except FileNotFoundError:
        print(f"Error: {local_conf_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating evaluate/config.yaml: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python change_conflict.py <c>")
        sys.exit(1)
    
    try:
        c = sys.argv[1]
        change_conflict(int(c))
    except ValueError:
        print("Error: Argument must be a number")
        sys.exit(1)

if __name__ == "__main__":
    main()