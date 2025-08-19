import paramiko
from src.utils.logging import logger
import re

def identify_device_via_ssh(host: str, username: str, password: str) -> dict:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=username, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command("show version", timeout=10)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        result = output if output else error

        if not result:
            raise ValueError("No output from show version")

        if "PAN-OS" in result or "Palo Alto" in result:
            device_type = "palo_alto"
            stdin, stdout, stderr = client.exec_command("show system info", timeout=10)
            pa_output = stdout.read().decode('utf-8')
            model = re.search(r"model:\s*(.*?)\n", pa_output).group(1) if re.search(r"model:\s*(.*?)\n", pa_output) else "Unknown"
            version = re.search(r"sw-version:\s*(.*?)\n", pa_output).group(1) if re.search(r"sw-version:\s*(.*?)\n", pa_output) else "Unknown"
        elif "Check Point" in result or "Gaia" in result:
            device_type = "check_point"
            stdin, stdout, stderr = client.exec_command("show version all", timeout=10)
            cp_output = stdout.read().decode('utf-8')
            model = re.search(r"Product Name:\s*(.*?)\n", cp_output).group(1) if re.search(r"Product Name:\s*(.*?)\n", cp_output) else "Unknown"
            version = re.search(r"OS Major:\s*(.*?)\n", cp_output).group(1) if re.search(r"OS Major:\s*(.*?)\n", cp_output) else "Unknown"
        elif "FortiGate" in result or "Fortinet" in result:
            device_type = "fortinet"
            stdin, stdout, stderr = client.exec_command("get system status", timeout=10)
            ft_output = stdout.read().decode('utf-8')
            model = re.search(r"Hostname:\s*(.*?)\n", ft_output).group(1) if re.search(r"Hostname:\s*(.*?)\n", ft_output) else "Unknown"
            version = re.search(r"Version:\s*(.*?)\n", ft_output).group(1) if re.search(r"Version:\s*(.*?)\n", ft_output) else "Unknown"
        else:
            raise ValueError("Unknown device type")

        return {"type": device_type, "model": model, "version": version}
    except Exception as e:
        logger.error(f"Device identification failed: {e}")
        raise
    finally:
        client.close()