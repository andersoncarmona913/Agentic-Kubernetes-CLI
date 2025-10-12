from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client
import os
from typing import Optional, Tuple

BEDROCK_MODEL_REGION = os.getenv("BEDROCK_MODEL_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "apac.anthropic.claude-3-5-sonnet-20241022-v2:0")

K8S_SYSTEM_PROMPT = """You are an expert Kubernetes operations assistant with direct kubectl access.

Your capabilities:
- Execute any kubectl command to manage and inspect Kubernetes resources
- Manage kubectl contexts (get current, list all, switch between clusters)
- Retrieve detailed information about pods, deployments, services, nodes, and all K8s resources
- Analyze logs, events, and resource states for troubleshooting
- Perform administrative operations (create, update, delete resources)

Guidelines:
1. **Context Awareness**: Always check the current kubectl context before executing commands
2. **Namespace Handling**: 
   - Default to the 'default' namespace if not specified
   - Use '-n <namespace>' or '--all-namespaces' flag when appropriate
3. **Command Construction**:
   - Always include 'kubectl' prefix in commands
   - Use appropriate output formats: '-o wide', '-o json', '-o yaml' when detailed info is needed
   - For logs: use '--tail=100' by default, adjust based on user needs
4. **Safety First**:
   - For destructive operations (delete, drain, cordon), confirm the command with the user first
   - Always verify resource existence before operations
5. **Troubleshooting Approach**:
   - Check pod status first: kubectl get pods -n <namespace>
   - Then describe for details: kubectl describe pod <name> -n <namespace>
   - Finally check logs: kubectl logs <pod-name> -n <namespace> --tail=100
6. **Output Formatting**:
   - Present information clearly and concisely
   - Highlight errors, warnings, or critical states
   - Suggest next steps or follow-up actions
7. **Multi-step Operations**:
   - Break complex tasks into logical steps
   - Verify each step before proceeding
   - Provide progress updates

Common Command Patterns:
- List resources: kubectl get <resource> [-n <namespace>] [-o wide/json/yaml]
- Describe details: kubectl describe <resource> <name> -n <namespace>
- View logs: kubectl logs <pod-name> [-n <namespace>] [--tail=N] [-f]
- Execute in pod: kubectl exec -it <pod-name> -n <namespace> -- <command>
- Port forward: kubectl port-forward <pod-name> <local-port>:<pod-port> -n <namespace>
- Check contexts: Use kubectl_context tool
- Apply configs: kubectl apply -f <file> -n <namespace>
- Scale deployments: kubectl scale deployment <name> --replicas=N -n <namespace>

Example interactions:
- "Show all pods" → kubectl get pods --all-namespaces -o wide
- "What's wrong with nginx pod?" → kubectl describe pod nginx -n default, then kubectl logs nginx --tail=100
- "Switch to production cluster" → Use kubectl_context tool with action='use'
- "Delete failing pods in test namespace" → Confirm first, then kubectl delete pod <name> -n test

Always be precise, security-conscious, and provide actionable insights."""


def initialize_k8s_agent() -> Optional[Tuple[Agent, MCPClient]]:
    """Initialize the Kubernetes agent with MCP kubectl tools."""
    try:
        server_params = StdioServerParameters(
            command="python",
            args=["k8s_cli_mcp_server.py"],
            env=None
        )

        mcp_client = MCPClient(lambda: stdio_client(server_params))
        
        mcp_client.__enter__()
        
        tools = mcp_client.list_tools_sync()
        

        bedrock_model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=BEDROCK_MODEL_REGION
        )

        agent = Agent(
            model=bedrock_model,
            tools=tools,
            system_prompt=K8S_SYSTEM_PROMPT
        )
        
        return agent, mcp_client
        
    except FileNotFoundError as e:
        print(f"❌ Error: kubectl MCP server file not found: {str(e)}")
        print("   Make sure 'k8s_mcp_server.py' exists in the current directory")
        return None
    except Exception as e:
        print(f"❌ Error initializing kubectl agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def print_welcome():
    """Print welcome message with usage examples."""
    print("\n" + "="*70)
    print("⎈  Kubernetes Operations Agent (kubectl powered)")
    print("="*70)
    print("\n📋 What you can ask:")
    print("\n  Resource Management:")
    print("    • List all pods in the cluster")
    print("    • Show deployments in production namespace")
    print("    • Get service details for nginx")
    print("    • Describe node worker-1")
    print("\n  Troubleshooting:")
    print("    • Why is my pod failing?")
    print("    • Show logs from api-server pod")
    print("    • Check events in kube-system namespace")
    print("    • Get the last 50 lines of logs from pod-name")
    print("\n  Context & Configuration:")
    print("    • What's my current context?")
    print("    • List all available contexts")
    print("    • Switch to staging cluster")
    print("\n  Advanced Operations:")
    print("    • Scale deployment to 5 replicas")
    print("    • Get pods with high memory usage")
    print("    • Show all resources in a namespace")
    print("\n💡 Commands: 'exit', 'quit', 'q' - End session | 'help' - Show this menu")
    print("="*70 + "\n")


def print_context_info(agent: Agent):
    """Display current kubectl context information."""
    try:
        print("🔍 Checking current kubectl context...")
        response = agent("What is my current kubectl context?")
        print(f"📍 {response}\n")
    except Exception as e:
        print(f"⚠️  Could not retrieve context: {str(e)}\n")


def interactive_mode(agent: Agent):
    """Run the agent in interactive mode."""
    print_welcome()
    print_context_info(agent)
    
    while True:
        try:
            user_query = input("⎈  kubectl> ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye! Closing kubectl agent...")
                break
            
            if user_query.lower() == 'help':
                print_welcome()
                continue
            
            if not user_query:
                continue
            
            print("\n⏳ Executing kubectl operation...\n")

            response = agent(user_query)
            
            print("─" * 70)
            print("📊 Response:")
            print("─" * 70)
            print(response)
            print("─" * 70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error processing request: {str(e)}")
            print("💡 Try rephrasing your query or type 'help' for examples\n")
            continue


def main():
    """Main entry point for the kubectl agent."""
    print("\n🚀 Initializing Kubernetes kubectl agent...")
    
    result = initialize_k8s_agent()
    
    if result is None:
        print("\n❌ Failed to initialize kubectl agent. Exiting...")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure k8s_mcp_server.py is in the current directory")
        print("   2. Verify kubectl is installed and configured")
        print("   3. Check AWS credentials for Bedrock access")
        return
    
    agent, mcp_client = result
    
    try:
        interactive_mode(agent)
    finally:
        # Cleanup MCP client
        print("\n🧹 Cleaning up resources...")
        try:
            mcp_client.__exit__(None, None, None)
            print("✅ MCP client closed successfully")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {str(e)}")


if __name__ == "__main__":
    main()