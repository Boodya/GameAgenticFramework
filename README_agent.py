from game_framework import Agent, Goal
from game_framework import Environment, AgentFunctionCallingActionLanguage
from typing import List
import llm
import os
from tool_decorator import register_tool, PythonActionRegistry

llm.set_azure_env()

@register_tool(tags=["file_operations", "read"])
def read_project_file(name: str) -> str:
    """Reads and returns the content of a specified project file.

    Opens the file in read mode and returns its entire contents as a string.
    Raises FileNotFoundError if the file doesn't exist.

    Args:
        name: The name of the file to read

    Returns:
        The contents of the file as a string
    """
    with open(name, "r") as f:
        return f.read()
    
@register_tool(tags=["file_operations", "write"])
def write_project_file(name: str, content: str) -> None:
    """Writes the text content to a file in the current directory.

    Opens the file in write mode and writes the provided content to it.
    
    Args:
        name: The name of the file to write
        content: The text content to write to the file
        
    Returns:
        None
    """
    with open(name, "w") as f:
        f.write(content)

@register_tool(tags=["file_operations", "list"])
def list_project_files() -> List[str]:
    """Lists all Python files in the current project directory.

    Scans the current directory and returns a sorted list of all files
    that end with '.py'.

    Returns:
        A sorted list of Python filenames
    """
    return sorted([file for file in os.listdir(".")
                    if file.endswith(".py")])

@register_tool(tags=["system"], terminal=True)
def terminate(message: str) -> str:
    """Terminates the agent's execution with a final message.

    Args:
        message: The final message to return before terminating

    Returns:
        The message with a termination note appended
    """
    return f"{message}\nTerminating..."


# Define the agent's goals
goals = [
    Goal(priority=1,
            name="Gather Information",
            description="Read each file in the project in order to build a deep understanding of the project in order to write a README"),
    Goal(priority=1,
            name="Write README",
            description="Write a comprehensive README for the project based on the information gathered from the files"),
    Goal(priority=1,
            name="Terminate",
            description="Call terminate when done and provide a short summary of what was done")
]

# Create an agent instance with tag-filtered actions
agent = Agent(
    goals=goals,
    agent_language=AgentFunctionCallingActionLanguage(),
    # The ActionRegistry now automatically loads tools with these tags
    action_registry=PythonActionRegistry(tags=["file_operations", "system"]),
    generate_response=llm.generate_response,
    environment=Environment()
)

# Run the agent with user input
user_input = "Write a README for this project."
final_memory = agent.run(user_input)
print(final_memory.get_memories())