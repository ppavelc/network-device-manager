import paramiko
import re
from typing import Dict, Any
from src.utils.logging import logger

def parse_output_to_json(output: str, command: str) -> Dict[str, Any]:
    """
    Parse SSH command output into JSON based on common network device output patterns.
    Returns a dictionary with parsed data or raw output if parsing fails.
    """
    try:
        # Initialize result
        parsed = {"command": command, "parsed": {}, "raw": output}

        # Handle empty output
        if not output.strip():
            parsed["error"] = "No output received"
            return parsed

        # Example 1: Key-value pairs (e.g., "Version: 15.1", "Hostname: router1")
        key_value_pattern = re.compile(r"^(.*?)\s*:\s*(.*?)$", re.MULTILINE)
        key_value_matches = key_value_pattern.findall(output)
        if key_value_matches:
            for key, value in key_value_matches:
                parsed["parsed"][key.strip()] = value.strip()

        # Example 2: Tabular data (e.g., "show interfaces" with columns)
        lines = output.splitlines()
        if any("|" in line or "\t" in line for line in lines):  # Assume table if | or tabs present
            table_data = []
            headers = None
            for line in lines:
                line = line.strip()
                if not line or line.startswith(("#", "-")):
                    continue
                # Split by | or multiple spaces/tabs
                columns = [col.strip() for col in re.split(r"\s{2,}|\|", line) if col.strip()]
                if not headers:
                    headers = columns
                elif len(columns) == len(headers):
                    table_data.append(dict(zip(headers, columns)))
            if table_data:
                parsed["parsed"]["table"] = table_data

        # If no parsing applied, keep raw output
        if not parsed["parsed"]:
            parsed["parsed"] = {"raw_output": output}

        return parsed

    except Exception as e:
        logger.error(f"Error parsing output for command '{command}': {e}")
        return {"command": command, "error": str(e), "raw": output}

async def ssh_execute_commands(host: str, username: str, password: str, commands: list[str]) -> Dict[str, Dict[str, Any]]:
    """
    Execute a list of commands on a remote device via SSH using Paramiko.
    Returns a dictionary mapping commands to their parsed JSON outputs.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    output = {}

    try:
        # Connect to the device
        client.connect(hostname=host, username=username, password=password, timeout=10)
        logger.info(f"SSH connected to {host}")

        # Execute each command
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
            cmd_output = stdout.read().decode('utf-8').strip()
            cmd_error = stderr.read().decode('utf-8').strip()
            result = cmd_output if cmd_output else cmd_error
            # Parse output to JSON
            output[cmd] = parse_output_to_json(result, cmd)
            logger.debug(f"Command '{cmd}' executed on {host}: {output[cmd]}")

        return output

    except paramiko.AuthenticationException:
        logger.error(f"Authentication failed for {host}")
        raise Exception("Authentication failed")
    except paramiko.SSHException as ssh_err:
        logger.error(f"SSH error for {host}: {str(ssh_err)}")
        raise Exception(f"SSH error: {str(ssh_err)}")
    except Exception as e:
        logger.error(f"Error connecting to {host}: {str(e)}")
        raise Exception(f"Connection error: {str(e)}")
    finally:
        client.close()
        logger.info(f"SSH connection to {host} closed")