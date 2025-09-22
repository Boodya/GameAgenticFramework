from game_framework import Agent, Goal, Action, ActionRegistry
from game_framework import Environment, AgentFunctionCallingActionLanguage
from typing import List
import llm
import os

llm.set_azure_env()

# Define the agent's goals
goals = [
    Goal(priority=1, name="Gather Information", description="Read each file in the project"),
    Goal(priority=1, name="Terminate", description="Call the terminate call when you have read all the files" \
    " as a parameter for terminating action call you should provide a final message to the user with README content for the whole project."),
]

# Define the agent's language
agent_language = AgentFunctionCallingActionLanguage()

def read_project_file(name: str) -> str:
    with open(name, "r") as f:
        return f.read()

def list_project_files() -> List[str]:
    return sorted([file for file in os.listdir(".") if file.endswith(".py")])

def terminate_action(message: str) -> str:
    return f"{message}"

# Define the action registry and register some actions
action_registry = ActionRegistry()
action_registry.register(Action(
    name="list_project_files",
    function=list_project_files,
    description="Lists all files in the project.",
    parameters={},
    terminal=False
))
action_registry.register(Action(
    name="read_project_file",
    function=read_project_file,
    description="Reads a file from the project.",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    },
    terminal=False
))
action_registry.register(Action(
    name="terminate",
    function=terminate_action,
    description="Terminates the session and prints the message to the user.",
    parameters={
        "type": "object",
        "properties": {
            "message": {"type": "string"}
        },
        "required": []
    },
    terminal=True
))

# Define the environment
environment = Environment()

# Create an agent instance
agent = Agent(goals, agent_language, action_registry, llm.generate_response, environment)

# Run the agent with user input
user_input = "Write a README for this project."
final_memory = agent.run(user_input)
memories = final_memory.get_memories()
if isinstance(memories, list) and memories:
    last_memory = memories[-1]
else:
    last_memory = None
# Print the final memory
#print(memories)
print("\nTermination Message:\n", last_memory)