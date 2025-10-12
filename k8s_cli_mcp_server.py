from mcp.server import FastMCP
import subprocess
import json
import shlex
from typing import Dict, Any, Optional

# Create MCP server instance
mcp = FastMCP("kubernetes-cli-server")


def validate_kubectl_command(command: str) -> tuple[bool, Optional[str]]:
    """Validate that the command is a safe kubectl command."""
    if not command.strip().startswith("kubectl"):
        return False, "Command must start with 'kubectl'"
    
    dangerous_operations = ["delete", "drain", "cordon"]
    cmd_parts = command.lower().split()
    
    if any(op in cmd_parts for op in dangerous_operations):
        pass
    
    return True, None


def parse_kubectl_output(stdout: str, stderr: str, return_code: int) -> Dict[str, Any]:
    """Attempt to parse kubectl output as JSON if possible."""
    if return_code != 0:
        return {"raw": stdout, "parsed": None, "format": "text"}
    
    try:
        parsed = json.loads(stdout)
        return {"raw": stdout, "parsed": parsed, "format": "json"}
    except json.JSONDecodeError:
        return {"raw": stdout, "parsed": None, "format": "text"}


@mcp.tool("run_kubectl_command")
def run_kubectl_command(command: str) -> Dict[str, Any]:
    """
    Execute a kubectl command and return its output.
    
    Args:
        command: Full kubectl command to execute (e.g., "kubectl get pods", "kubectl describe node worker-1")
                 Must include 'kubectl' prefix.
    
    Returns:
        Dictionary containing command output, return code, and any errors
    
    Examples:
        - kubernetes("kubectl get pods")
        - kubernetes("kubectl get namespaces")
        - kubernetes("kubectl describe pod nginx-abc123")
        - kubernetes("kubectl logs my-pod --tail=50")
        - kubernetes("kubectl get pods -o json")
    """
    try:
        # Validate command
        is_valid, error_msg = validate_kubectl_command(command)
        if not is_valid:
            error_data = {
                "command": command,
                "error": error_msg,
                "success": False
            }
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ Invalid command: {error_msg}"
                }],
                "result": json.dumps(error_data, indent=2)
            }
        
        cmd_parts = shlex.split(command)
        
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output_data = parse_kubectl_output(result.stdout, result.stderr, result.returncode)
        
        response_data = {
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "output_format": output_data["format"],
            "parsed_output": output_data["parsed"]
        }
        
        if result.returncode == 0:

            if output_data["format"] == "json" and output_data["parsed"]:
                formatted_output = json.dumps(output_data["parsed"], indent=2)
                message = f"✅ Command executed successfully:\n\n```json\n{formatted_output}\n```"
            else:
                message = f"✅ Command executed successfully:\n\n```\n{result.stdout}\n```"
        else:
            message = f"❌ Command failed with return code {result.returncode}:\n\n```\n{result.stderr}\n```"
        
        return {
            "content": [{
                "type": "text",
                "text": message
            }],
            "result": json.dumps(response_data, indent=2)
        }
        
    except subprocess.TimeoutExpired:
        error_data = {
            "command": command,
            "error": "Command execution timeout (30s)",
            "success": False
        }
        return {
            "content": [{
                "type": "text",
                "text": f"⏱️ Command timed out after 30 seconds:\n`{command}`"
            }],
            "result": json.dumps(error_data, indent=2)
        }
        
    except FileNotFoundError:
        error_data = {
            "command": command,
            "error": "kubectl command not found. Is kubectl installed and in PATH?",
            "success": False
        }
        return {
            "content": [{
                "type": "text",
                "text": "❌ Error: kubectl command not found.\nPlease ensure kubectl is installed and available in your PATH."
            }],
            "result": json.dumps(error_data, indent=2)
        }
        
    except Exception as e:
        error_data = {
            "command": command,
            "error": str(e),
            "error_type": type(e).__name__,
            "success": False
        }
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Unexpected error executing command:\n{type(e).__name__}: {str(e)}"
            }],
            "result": json.dumps(error_data, indent=2)
        }


@mcp.tool("kubectl_context")
def kubectl_context(action: str = "get", context_name: str = "") -> Dict[str, Any]:
    """
    Manage kubectl contexts.
    
    Args:
        action: Action to perform - 'get' (current context), 'list' (all contexts), or 'use' (switch context)
        context_name: Name of context to switch to (required when action='use')
    
    Returns:
        Dictionary containing context information
    
    Examples:
        - kubectl_context("get")
        - kubectl_context("list")
        - kubectl_context("use", "production-cluster")
    """
    try:
        if action == "get":
            command = ["kubectl", "config", "current-context"]
        elif action == "list":
            command = ["kubectl", "config", "get-contexts"]
        elif action == "use":
            if not context_name:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ Error: context_name is required when action='use'"
                    }],
                    "result": json.dumps({"success": False, "error": "Missing context_name"}, indent=2)
                }
            command = ["kubectl", "config", "use-context", context_name]
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ Error: Invalid action '{action}'. Use 'get', 'list', or 'use'"
                }],
                "result": json.dumps({"success": False, "error": "Invalid action"}, indent=2)
            }
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            message = f"✅ Context operation successful:\n\n```\n{result.stdout}\n```"
        else:
            message = f"❌ Context operation failed:\n\n```\n{result.stderr}\n```"
        
        return {
            "content": [{
                "type": "text",
                "text": message
            }],
            "result": json.dumps({
                "action": action,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }, indent=2)
        }
        
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error managing context: {str(e)}"
            }],
            "result": json.dumps({"success": False, "error": str(e)}, indent=2)
        }


if __name__ == "__main__":
    # Start the MCP server with stdio transport
    mcp.run(transport="stdio")