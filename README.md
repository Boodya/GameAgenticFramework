Project: Agent GAME Framework

Overview

This repository contains a lightweight agent "GAME" (Goals, Actions, Memory, Environment) framework that demonstrates how to build a function-calling agent backed by an LLM. It includes:

- a minimal agent runtime and prompt construction layer (game_framework.py)
- an LLM wrapper using litellm (llm.py)
- a simple tool-registration decorator + action registry (tool_decorator.py)
- a runnable example that registers file-system and termination tools and runs the agent (README_agent.py)

The design focuses on making it easy to register Python functions as "tools" (with automatic parameter schema generation), create goals for the agent, maintain working memory, and let the LLM choose actions via function-calling.

Contents

- README_agent.py: Example usage that registers file operations (read, write, list) and a terminal 'terminate' tool, sets up goals, creates an Agent, and runs it with a one-line task.
- game_framework.py: Core classes and agent loop. Key classes:
  - Goal (dataclass): prioritized goal description.
  - Memory: simple conversation / working memory store used to build prompts.
  - Environment: executes an Action and formats results.
  - AgentLanguage (and AgentFunctionCallingActionLanguage): builds prompts (system goals, memory messages, and a tools list) and parses LLM responses.
  - Agent: the main loop that prompts the LLM, chooses and executes actions, updates memory, and optionally terminates.
- llm.py: LLM integration and helper classes:
  - Prompt dataclass: holds messages and tools used to call the LLM.
  - set_ollama_env / set_azure_env: convenience functions to configure environment variables for litellm backends.
  - generate_response / generate_response_raw: call litellm.completion and translate function-calling responses into a JSON {"tool":..., "args":...} string.
  - ChatThread and ConsoleChat: small utilities for conversational usage.
- tool_decorator.py: Utility to register Python functions as tools:
  - register_tool decorator: inspects function signature and auto-generates a JSON-schema-like parameters object. It stores metadata in a global tools dict.
  - Action / ActionRegistry / PythonActionRegistry: runtime Action wrapper and registries that filter tools by tag and can mark a tool as terminal (agent will stop after executing a terminal tool).

Quickstart

1. Install dependencies

This project uses litellm for LLM calls. Install it and any other dependencies used in your environment:

pip install litellm

(If you plan to use Azure, Ollama, or other backends, configure your local environment according to those backends.)

2. Configure your LLM backend

- Ollama example:
  - Call llm.set_ollama_env() programmatically, or set these env vars manually:
    - litellm_env=ollama
    - OLLAMA_MODEL_NAME=ollama/gpt-oss:20b

- Azure OpenAI example (convenience helper in code):
  - Call llm.set_azure_env() which sets these env vars:
    - litellm_env=azure
    - AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION, AZURE_DEPLOYMENT_NAME, AZURE_MODEL_NAME
  - NOTE: README_agent.py currently calls set_azure_env() and the file contains a hard-coded example API key and endpoint. Do NOT ship or commit real credentials — replace or set your own secure environment variables instead.

3. Run the example agent

python README_agent.py

This script will:
- register file-based tools (read_project_file, write_project_file, list_project_files) and a terminate tool via @register_tool
- set goals for the agent (gather information, write README, terminate)
- create a PythonActionRegistry that only exposes tools tagged with file_operations and system
- run the agent loop with a single user instruction: "Write a README for this project."

How tools are registered and used

- Decorator: Use @register_tool(tags=[...], terminal=False) on any Python function to register it as a tool. The decorator inspects the function signature and docstring to build the parameter schema automatically.
- Tags: Tools can be grouped by tags. PythonActionRegistry(tags=["file_operations","system"]) will only expose tools that have at least one of those tags — this allows creating action subsets for different agent capabilities.
- Terminal tools: Mark a tool as terminal if the agent should stop after invoking it (e.g., terminate()). The registry can detect and treat terminal actions specially.
- Action calling: The AgentLanguage constructs a Prompt where tools are provided using the function-calling format. The LLM is expected to return a tool call. llm.generate_response converts function-calling tool calls into a JSON string like: {"tool": "tool_name", "args": {...}} which game_framework.Agent.parse_response consumes to find and invoke the Action.

Prompt construction and Memory

- Goals are formatted as a system message that concatenates goal names and descriptions.
- Memory stores a chronological list of messages and environment results. When building the prompt the memory items are mapped to user/assistant messages so the LLM has the conversation and environment history available.

Extending the framework

- Add tools: Use @register_tool on any function and include proper type hints for better parameter schemas.
- New agent languages: Create a subclass of AgentLanguage to implement different prompt formats or parsing strategies.
- Different action registries: Build custom registries to load tools from other sources (external services, or runtime plugin systems).

Security and best practices

- Never commit real API keys or secrets. Replace the sample set_azure_env() credentials in llm.py with environment-based configuration or secure secret storage.
- Validate tool arguments in your own tool functions. The framework provides a parameter schema for tool calling but does not itself validate runtime semantics beyond invoking the Python function.

Limitations and notes

- The parse_response implementation in AgentFunctionCallingActionLanguage expects that the LLM returns a JSON-parseable string or it defaults to invoking the terminate tool with the raw response.
- The generate_response pipeline uses litellm.completion; if you switch to another library or provider, adapt llm.generate_response and generate_response_raw.

Contributing

Contributions are welcome. Suggested areas:
- Add unit tests for prompt construction and tool schema generation
- Add richer parameter schemas (arrays of typed objects, nested schemas, etc.)
- Add better error handling, retries, and prompt repair strategies when parsing fails

License

This repository does not include an explicit license file. If you intend to open-source, add a LICENSE (MIT, Apache 2.0, etc.).

Contact

If you have questions about the design or need help extending the framework, open an issue or reach out to the repository owner.
