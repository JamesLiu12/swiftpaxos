import sys
import yaml
from .config_loader import ConfigLoader
from evaluate.node import Node
import os

proto_config = {
    'paxos': {
        'leaderless': 'false',
        'fast': 'false',
    },
    'swiftpaxos': {
        'leaderless': 'false',
        'fast': 'true',
    },
    'eppaxos': {
        'leaderless': 'true',
        'fast': 'false',
    },
}

def change_proto(proto: str):
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
            if line.strip().startswith('protocol:'):
                lines[i] = f'protocol: {proto}\n'
            elif line.strip().startswith('leaderless:'):
                lines[i] = f'leaderless: {proto_config[proto]["leaderless"]}\n'
            elif line.strip().startswith('fast:'):
                lines[i] = f'fast:       {proto_config[proto]["fast"]}\n'
        
        # Write back to local.conf
        with open(local_conf_path, 'w') as f:
            f.writelines(lines)
        
        print(f"Updated local.conf - protocol: {proto}")
        
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
        config['protocol'] = proto
        
        # Write back to evaluate/config.yaml
        with open(config_yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Updated evaluate/config.yaml - protocol: {proto}")
        
    except FileNotFoundError:
        print(f"Error: {local_conf_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating evaluate/config.yaml: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python change_proto.py <c>")
        sys.exit(1)
    
    p = sys.argv[1]
    change_proto(p)

if __name__ == "__main__":
    main()