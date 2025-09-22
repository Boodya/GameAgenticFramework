import json
import os
from litellm import completion
from typing import List, Dict
from dataclasses import dataclass, field
#litellm._turn_on_debug()

@dataclass
class Prompt:
    messages: List[Dict] = field(default_factory=list)
    tools: List[Dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)  # Fixing mutable default 
    max_tokens: int = None

def set_ollama_env():
    """Set environment variables for Ollama configuration"""
    os.environ["litellm_env"] = "ollama"
    os.environ["OLLAMA_MODEL_NAME"] = "ollama/gpt-oss:20b"

def set_azure_env():
    """Set environment variables for Azure OpenAI configuration"""
    os.environ["litellm_env"] = "azure"
    os.environ["AZURE_API_KEY"] = ""
    os.environ["AZURE_API_BASE"] = ""
    os.environ["AZURE_API_VERSION"] = "2024-12-01-preview"
    os.environ["AZURE_DEPLOYMENT_NAME"] = "gpt-5-mini"
    os.environ["AZURE_MODEL_NAME"] = "azure/gpt-5-mini"

def generate_response(prompt: Prompt) -> str:
    """Call LLM to get response"""

    result = None

    if not prompt.tools:
        response = generate_response_raw(prompt.messages, maxTokens=prompt.max_tokens)
        result = response.choices[0].message.content
    else:
        response = generate_response_raw(prompt.messages, maxTokens=prompt.max_tokens, tools=prompt.tools)

        if response.choices[0].message.tool_calls:
            tool = response.choices[0].message.tool_calls[0]
            result = {
                "tool": tool.function.name,
                "args": json.loads(tool.function.arguments),
            }
            result = json.dumps(result)
        else:
            result = response.choices[0].message.content
            
    return result

def generate_response_raw(messages: List[Dict], maxTokens: int=None, tools: List[Dict]=None) -> any:
    """Call LLM to get response object"""
    env = os.environ.get("litellm_env", "azure")
    if env == "azure":
        response = completion(
            model=os.environ["AZURE_MODEL_NAME"],
            api_base=os.environ["AZURE_API_BASE"],
            api_key=os.environ["AZURE_API_KEY"],
            api_version=os.environ["AZURE_API_VERSION"],
            max_tokens=maxTokens,
            tools=tools,
            messages=messages
        )
    if env == "ollama":
        response = completion(
            model=os.environ["OLLAMA_MODEL_NAME"],            
            tools=tools,
            messages=messages
        )

    # You can add other environments like OpenAI here
    return response

class ChatThread:
    """Class to handle conversational history for AI interactions."""
    
    def __init__(self, existingMessages: List[Dict] = None):
        """Initialize with preconfigured messages or an empty list."""
        if existingMessages is None:
            self.messages: List[Dict] = []
        else:
            self.messages: List[Dict] = existingMessages
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history.
        
        Args:
            role (str): The role of the message sender (e.g., 'user', 'assistant').
            content (str): The content of the message.
        """
        self.messages.append({"role": role, "content": content})
    
    def get_history(self) -> List[Dict]:
        """Get the full conversation history.
        
        Returns:
            List[Dict]: The list of messages.
        """
        return self.messages
    
    def clear_history(self):
        """Clear the conversation history."""
        self.messages = []
    
    def send_message(self, message: str, maxTokens: int = None) -> str:
        """Generate a response using the current conversation history.
        
        Args:
            maxTokens (int): Maximum tokens for the response.
        
        Returns:
            str: The generated response content.
        """
        self.add_message("user", message)
        response = generate_response_raw(self.messages, maxTokens)
        self.add_message("assistant", response.choices[0].message.content)
        return response.choices[0].message.content

class ConsoleChat:
    """Class to facilitate console-based chat with AI."""
    
    def __init__(self, existingMessages: List[Dict] = None):
        """Initialize with preconfigured messages or an empty list."""
        self.chat: ChatThread = ChatThread(existingMessages)

    def start_chat(self):
        """Start an interactive console chat session."""
        print("Starting console chat. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting chat.")
                break
            assistant_message = self.chat.send_message(user_input)
            print(f"AI: {assistant_message}")
