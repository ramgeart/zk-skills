#!/usr/bin/env python3
"""
SSH Sheller - Helper script for SSH operations using native ssh command.
Supports connections, command execution, port forwarding, SCP, and server management.
"""

import argparse
import os
import platform
import subprocess
import sys
import yaml
from pathlib import Path


def find_config_file(skill_root=None, create_default=False):
    """
    Find sheller.yaml config file.
    Search order:
    1. Skill root directory (if provided)
    2. ~/.ssh/sheller.yaml (or %USERPROFILE%/.ssh/sheller.yaml on Windows)
    
    Args:
        skill_root: Path to skill root directory
        create_default: If True, create default config if not found
    
    Returns: Path to config file or None if not found
    """
    locations = []
    
    # Check skill root first
    if skill_root:
        skill_config = Path(skill_root) / "sheller.yaml"
        locations.append(skill_config)
    
    # Check ~/.ssh/ (works on Windows via Path and expanduser)
    ssh_dir = Path.home() / ".ssh"
    user_config = ssh_dir / "sheller.yaml"
    locations.append(user_config)
    
    # Find existing config
    for loc in locations:
        if loc.exists():
            return loc
    
    # Create default if requested
    if create_default:
        print("No configuration file found.")
        print(f"\nWhere would you like to create the config file?")
        print(f"1. {locations[0]} (skill directory)")
        print(f"2. {locations[-1]} (user SSH directory)")
        
        choice = input("\nEnter choice (1 or 2, default: 2): ").strip() or "2"
        
        if choice == "1" and skill_root:
            config_path = locations[0]
        else:
            config_path = locations[-1]
            # Ensure .ssh directory exists
            ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Create default config
        default_config = {"servers": {}}
        save_config(config_path, default_config)
        print(f"\nCreated empty config at: {config_path}")
        return config_path
    
    return None


def load_config(config_path):
    """Load and parse YAML config file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {"servers": {}}


def save_config(config_path, config):
    """Save configuration to YAML file."""
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get_server_config(config, server_name):
    """
    Get server configuration by name.
    Supports nested structure with 'servers' key or flat structure.
    """
    servers = config.get('servers', config)
    
    if server_name not in servers:
        available = ', '.join(servers.keys()) if servers else "(none)"
        raise ValueError(f"Server '{server_name}' not found. Available: {available}")
    
    server = servers[server_name]
    
    # Handle shorthand notation: just a hostname string
    if isinstance(server, str):
        return {'host': server, 'user': None, 'port': 22}
    
    return {
        'host': server.get('host'),
        'user': server.get('user'),
        'port': server.get('port', 22),
        'key_file': server.get('key_file'),
        'password': server.get('password'),
        'options': server.get('options', [])
    }


def generate_ssh_key(key_path, key_type="ed25519", comment=None):
    """
    Generate a new SSH key pair using ed25519 (preferred).
    
    Args:
        key_path: Path where the private key will be saved
        key_type: Key type (default: ed25519)
        comment: Comment for the key (default: user@hostname)
    
    Returns: True if successful, False otherwise
    """
    key_path = Path(key_path).expanduser()
    
    # Don't overwrite existing key
    if key_path.exists():
        print(f"Error: Key already exists at {key_path}")
        return False
    
    # Ensure parent directory exists
    key_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    if comment is None:
        comment = f"{os.getlogin()}@{platform.node()}"
    
    cmd = [
        "ssh-keygen",
        "-t", key_type,
        "-f", str(key_path),
        "-C", comment,
        "-N", ""  # No passphrase (user can add later if needed)
    ]
    
    print(f"Generating {key_type} key pair...")
    print(f"  Private key: {key_path}")
    print(f"  Public key: {key_path}.pub")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        # Set restrictive permissions on private key (Windows ignores this mostly)
        key_path.chmod(0o600)
        print(f"\nKey generated successfully!")
        print(f"\nTo use this key on a server, copy the public key:")
        print(f"  ssh-copy-id -i {key_path}.pub user@server")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating key: {e}")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print("Error: ssh-keygen not found. Please install OpenSSH.")
        return False


def interactive_add_server(config, config_path):
    """Interactively add a new server to configuration."""
    print("\n=== Add New Server ===\n")
    
    name = input("Server name (e.g., 'prod-web'): ").strip()
    if not name:
        print("Error: Server name is required.")
        return False
    
    if name in config.get('servers', {}):
        overwrite = input(f"Server '{name}' already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Cancelled.")
            return False
    
    host = input("Hostname or IP: ").strip()
    if not host:
        print("Error: Hostname is required.")
        return False
    
    user = input("Username (default: current user): ").strip() or None
    
    port_input = input("SSH port (default: 22): ").strip()
    port = int(port_input) if port_input else 22
    
    # Key file handling
    key_file = None
    use_key = input("Use SSH key authentication? (Y/n): ").strip().lower() != 'n'
    
    if use_key:
        print("\nSSH Key options:")
        print("1. Use existing key file")
        print("2. Generate new ed25519 key pair (recommended)")
        
        key_choice = input("\nChoice (1 or 2, default: 2): ").strip() or "2"
        
        if key_choice == "2":
            # Generate new key
            default_key_dir = Path.home() / ".ssh"
            key_name = input(f"Key name (default: {name}_ed25519): ").strip() or f"{name}_ed25519"
            key_path = default_key_dir / key_name
            
            if generate_ssh_key(key_path, key_type="ed25519"):
                key_file = str(key_path)
        else:
            # Use existing key
            key_path = input("Path to private key file (e.g., ~/.ssh/id_ed25519): ").strip()
            if key_path:
                key_file = key_path
    
    # Password (optional, for backup)
    password = None
    if not key_file:
        use_password = input("Store password in config? (y/N): ").strip().lower() == 'y'
        if use_password:
            password = input("Password: ")  # Note: this is visible, use getpass for hidden input
    
    # Build server config
    server_config = {
        'host': host,
    }
    
    if user:
        server_config['user'] = user
    if port != 22:
        server_config['port'] = port
    if key_file:
        server_config['key_file'] = key_file
    if password:
        server_config['password'] = password
    
    # Add to config
    if 'servers' not in config:
        config['servers'] = {}
    
    config['servers'][name] = server_config
    save_config(config_path, config)
    
    print(f"\nServer '{name}' added successfully!")
    print(f"Configuration saved to: {config_path}")
    
    if key_file and not Path(key_file).exists():
        print(f"\nNote: Key file {key_file} does not exist yet.")
    
    return True


def list_servers(config):
    """List all configured servers."""
    servers = config.get('servers', {})
    
    if not servers:
        print("No servers configured.")
        return
    
    print("\n=== Configured Servers ===\n")
    print(f"{'Name':<20} {'Host':<25} {'User':<15} {'Auth':<10}")
    print("-" * 75)
    
    for name, server in servers.items():
        if isinstance(server, str):
            host = server
            user = "(default)"
            auth = "default"
        else:
            host = server.get('host', 'N/A')
            user = server.get('user') or "(default)"
            if server.get('key_file'):
                auth = "key"
            elif server.get('password'):
                auth = "password"
            else:
                auth = "default"
        
        print(f"{name:<20} {host:<25} {user:<15} {auth:<10}")
    
    print()


def remove_server(config, config_path, server_name):
    """Remove a server from configuration."""
    if 'servers' not in config or server_name not in config['servers']:
        print(f"Error: Server '{server_name}' not found.")
        return False
    
    confirm = input(f"Remove server '{server_name}'? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return False
    
    del config['servers'][server_name]
    save_config(config_path, config)
    print(f"Server '{server_name}' removed.")
    return True


def show_server_details(config, server_name):
    """Show detailed configuration for a server."""
    try:
        servers = config.get('servers', {})
        if server_name not in servers:
            print(f"Error: Server '{server_name}' not found.")
            return
        
        server = servers[server_name]
        
        print(f"\n=== Server: {server_name} ===\n")
        
        if isinstance(server, str):
            print(f"Host: {server}")
            print("(using defaults for all other settings)")
        else:
            print(f"Host: {server.get('host', 'N/A')}")
            print(f"User: {server.get('user') or '(default)'}")
            print(f"Port: {server.get('port', 22)}")
            
            if server.get('key_file'):
                key_path = Path(server['key_file']).expanduser()
                print(f"Key file: {server['key_file']}")
                print(f"  -> Resolved: {key_path}")
                print(f"  -> Exists: {key_path.exists()}")
            
            if server.get('password'):
                print(f"Password: {'*' * len(server['password'])}")
            
            if server.get('options'):
                print(f"SSH Options: {', '.join(server['options'])}")
        
        print()
        
    except Exception as e:
        print(f"Error: {e}")


def build_ssh_command(server_config, command=None, tunnel_local=None, tunnel_remote=None, tunnel_host=None):
    """
    Build SSH command based on configuration and operation.
    
    Args:
        server_config: Server configuration dict
        command: Command to execute remotely (None for interactive)
        tunnel_local: Local port for tunnel (-L)
        tunnel_remote: Remote port for tunnel
        tunnel_host: Host to tunnel to (default: localhost)
    """
    user = server_config.get('user')
    host = server_config['host']
    port = server_config.get('port', 22)
    key_file = server_config.get('key_file')
    options = server_config.get('options', [])
    
    # Build base command
    cmd_parts = ['ssh']
    
    # Add port if not default
    if port != 22:
        cmd_parts.extend(['-p', str(port)])
    
    # Add key file if specified
    if key_file:
        # Expand ~ to home directory
        key_path = Path(key_file).expanduser()
        cmd_parts.extend(['-i', str(key_path)])
    
    # Add custom SSH options
    for opt in options:
        cmd_parts.extend(['-o', opt])
    
    # Add tunnel configuration if requested
    if tunnel_local is not None:
        tunnel_target = tunnel_host or 'localhost'
        cmd_parts.extend(['-L', f'{tunnel_local}:{tunnel_target}:{tunnel_remote}'])
    
    # Build connection string
    if user:
        target = f'{user}@{host}'
    else:
        target = host
    
    cmd_parts.append(target)
    
    # Add command if provided
    if command:
        cmd_parts.append(command)
    
    return cmd_parts


def build_scp_command(server_config, local_path, remote_path, upload=True):
    """
    Build SCP command for file transfer.
    
    Args:
        server_config: Server configuration dict
        local_path: Local file path
        remote_path: Remote file path
        upload: True to upload (local->remote), False to download (remote->local)
    """
    user = server_config.get('user')
    host = server_config['host']
    port = server_config.get('port', 22)
    key_file = server_config.get('key_file')
    
    cmd_parts = ['scp']
    
    # Add port
    if port != 22:
        cmd_parts.extend(['-P', str(port)])  # Note: scp uses -P (uppercase)
    
    # Add key file
    if key_file:
        key_path = Path(key_file).expanduser()
        cmd_parts.extend(['-i', str(key_path)])
    
    # Build remote path
    if user:
        remote_target = f'{user}@{host}:{remote_path}'
    else:
        remote_target = f'{host}:{remote_path}'
    
    # Source and destination
    if upload:
        cmd_parts.extend([local_path, remote_target])
    else:
        cmd_parts.extend([remote_target, local_path])
    
    return cmd_parts


def execute_command(cmd_parts, use_shell=False):
    """Execute the SSH command."""
    print(f"Executing: {' '.join(cmd_parts)}")
    
    # On Windows, we might need shell=True for some commands
    if platform.system() == 'Windows' and use_shell:
        cmd = ' '.join(cmd_parts)
        return subprocess.call(cmd, shell=True)
    else:
        return subprocess.call(cmd_parts)


def main():
    parser = argparse.ArgumentParser(description='SSH Sheller - SSH helper')
    parser.add_argument('--skill-root', help='Path to skill root directory')
    parser.add_argument('--config', help='Path to config file (overrides auto-discovery)')
    
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # Init action (create initial config)
    init_parser = subparsers.add_parser('init', help='Initialize configuration file')
    init_parser.add_argument('--location', choices=['skill', 'home'], 
                             help='Where to create config (default: ask)')
    
    # Add-server action
    add_parser = subparsers.add_parser('add-server', help='Add a new server interactively')
    
    # List-servers action
    list_parser = subparsers.add_parser('list-servers', help='List configured servers')
    
    # Show-server action
    show_parser = subparsers.add_parser('show-server', help='Show server details')
    show_parser.add_argument('server_name', help='Server name')
    
    # Remove-server action
    remove_parser = subparsers.add_parser('remove-server', help='Remove a server')
    remove_parser.add_argument('server_name', help='Server name')
    
    # Generate-key action
    keygen_parser = subparsers.add_parser('generate-key', help='Generate new SSH key pair (ed25519)')
    keygen_parser.add_argument('key_path', help='Path for the new key (e.g., ~/.ssh/mykey)')
    keygen_parser.add_argument('--comment', help='Key comment (default: user@hostname)')
    
    # Connect action (interactive SSH)
    connect_parser = subparsers.add_parser('connect', help='Interactive SSH connection')
    connect_parser.add_argument('server', help='Server name from config')
    
    # Exec action (run command)
    exec_parser = subparsers.add_parser('exec', help='Execute remote command')
    exec_parser.add_argument('server', help='Server name from config')
    exec_parser.add_argument('command', help='Command to execute')
    
    # Tunnel action
    tunnel_parser = subparsers.add_parser('tunnel', help='Create SSH tunnel')
    tunnel_parser.add_argument('server', help='Server name from config')
    tunnel_parser.add_argument('--local', '-l', type=int, required=True, help='Local port')
    tunnel_parser.add_argument('--remote', '-r', type=int, required=True, help='Remote port')
    tunnel_parser.add_argument('--host', default='localhost', help='Target host for tunnel (default: localhost)')
    
    # SCP upload action
    upload_parser = subparsers.add_parser('upload', help='Upload file via SCP')
    upload_parser.add_argument('server', help='Server name from config')
    upload_parser.add_argument('local', help='Local file path')
    upload_parser.add_argument('remote', help='Remote destination path')
    
    # SCP download action
    download_parser = subparsers.add_parser('download', help='Download file via SCP')
    download_parser.add_argument('server', help='Server name from config')
    download_parser.add_argument('remote', help='Remote file path')
    download_parser.add_argument('local', help='Local destination path')
    
    # Raw action (pass any ssh arguments)
    raw_parser = subparsers.add_parser('raw', help='Raw SSH with custom arguments')
    raw_parser.add_argument('server', help='Server name from config')
    raw_parser.add_argument('ssh_args', nargs='*', help='Additional SSH arguments')
    
    args = parser.parse_args()
    
    # Handle init action (no config needed)
    if args.action == 'init':
        locations = []
        if args.skill_root:
            locations.append(Path(args.skill_root) / "sheller.yaml")
        locations.append(Path.home() / ".ssh" / "sheller.yaml")
        
        # Determine location
        if args.location == 'skill' and args.skill_root:
            config_path = locations[0]
        elif args.location == 'home':
            config_path = locations[-1]
            config_path.parent.mkdir(mode=0o700, exist_ok=True)
        else:
            # Ask user
            print("Where would you like to create the config file?")
            for i, loc in enumerate(locations, 1):
                print(f"{i}. {loc}")
            choice = input(f"\nEnter choice (1-{len(locations)}, default: {len(locations)}): ").strip() or str(len(locations))
            config_path = locations[int(choice) - 1]
            if 'home' in str(config_path).lower() or '.ssh' in str(config_path):
                config_path.parent.mkdir(mode=0o700, exist_ok=True)
        
        if config_path.exists():
            print(f"Config already exists at: {config_path}")
        else:
            save_config(config_path, {"servers": {}})
            print(f"Created empty config at: {config_path}")
        return 0
    
    # Handle generate-key action (no config needed)
    if args.action == 'generate-key':
        success = generate_ssh_key(args.key_path, key_type="ed25519", comment=args.comment)
        return 0 if success else 1
    
    # Find config file
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
    else:
        config_path = find_config_file(args.skill_root, create_default=False)
        
        if not config_path:
            print("=" * 60)
            print("SSH Sheller - Bootstrap")
            print("=" * 60)
            print("\nNo configuration file found.")
            print("\nWould you like to:")
            print("1. Create a new configuration file")
            print("2. Specify an existing config file path")
            print("3. Exit")
            
            choice = input("\nEnter choice (1-3, default: 1): ").strip() or "1"
            
            if choice == "2":
                custom_path = input("Enter config file path: ").strip()
                config_path = Path(custom_path)
                if not config_path.exists():
                    print(f"File not found: {config_path}")
                    sys.exit(1)
            elif choice == "3":
                print("Exiting.")
                sys.exit(0)
            else:
                # Create new config
                config_path = find_config_file(args.skill_root, create_default=True)
                if not config_path:
                    sys.exit(1)
                
                # Ask if user wants to add first server
                add_first = input("\nWould you like to add your first server now? (Y/n): ").strip().lower() != 'n'
                if add_first:
                    config = load_config(config_path)
                    interactive_add_server(config, config_path)
                
                print("\nYou can now use the skill. Examples:")
                print(f"  python ssh_sheller.py <server> connect")
                print(f"  python ssh_sheller.py <server> exec 'ls -la'")
                return 0
    
    # Load config
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using config: {config_path}")
    
    # Handle management actions that don't need server
    if args.action == 'add-server':
        interactive_add_server(config, config_path)
        return 0
    
    if args.action == 'list-servers':
        list_servers(config)
        return 0
    
    if args.action == 'show-server':
        show_server_details(config, args.server_name)
        return 0
    
    if args.action == 'remove-server':
        remove_server(config, config_path, args.server_name)
        return 0
    
    # Handle SSH operations (need valid server)
    if args.action is None:
        parser.print_help()
        return 0
    
    # Get server config
    try:
        server_config = get_server_config(config, args.server)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"\nRun 'list-servers' to see available servers.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Build command based on action
    if args.action == 'connect':
        cmd = build_ssh_command(server_config)
        sys.exit(execute_command(cmd))
    
    elif args.action == 'exec':
        cmd = build_ssh_command(server_config, command=args.command)
        sys.exit(execute_command(cmd))
    
    elif args.action == 'tunnel':
        cmd = build_ssh_command(
            server_config,
            tunnel_local=args.local,
            tunnel_remote=args.remote,
            tunnel_host=args.host
        )
        print(f"Creating tunnel: local:{args.local} -> {args.host}:{args.remote}")
        print("Press Ctrl+C to close tunnel")
        sys.exit(execute_command(cmd))
    
    elif args.action == 'upload':
        cmd = build_scp_command(server_config, args.local, args.remote, upload=True)
        sys.exit(execute_command(cmd))
    
    elif args.action == 'download':
        cmd = build_scp_command(server_config, args.local, args.remote, upload=False)
        sys.exit(execute_command(cmd))
    
    elif args.action == 'raw':
        cmd = build_ssh_command(server_config)
        cmd.extend(args.ssh_args)
        sys.exit(execute_command(cmd))
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    main()
