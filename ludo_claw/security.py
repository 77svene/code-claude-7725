import os

class SecurityGate:
    """
    Enforces local-first security policies.
    Ensures that high-risk tools like BashTool and FileEditTool
    only execute in the local environment and not on a remote server.
    """
    def __init__(self):
        # We define "local" environment based on environment variables or specific configurations.
        # For Ludo-Claw, we assume the environment is local unless a remote flag is set.
        self.is_local_environment = os.getenv("LUDO_CLAW_REMOTE_EXECUTION", "false").lower() == "false"

    def authorize_tool_execution(self, tool_name: str) -> bool:
        """
        Authorizes the execution of a tool based on the security policy.
        """
        high_risk_tools = ["BashTool", "FileEditTool", "Bash", "FileEdit"]

        if tool_name in high_risk_tools:
            if not self.is_local_environment:
                print(f"SECURITY ALERT: Unauthorized attempt to run {tool_name} in a remote environment.")
                return False

        return True

    def execute_with_gate(self, tool_name: str, execution_callback, *args, **kwargs):
        """
        Executes a tool only if it passes the security gate.
        """
        if self.authorize_tool_execution(tool_name):
            return execution_callback(*args, **kwargs)
        else:
            raise PermissionError(f"Execution of {tool_name} blocked by SecurityGate (Local-Only).")
