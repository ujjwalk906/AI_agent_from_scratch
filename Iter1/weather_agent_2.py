## two lists -
## 1. List of messages
## 2. List of completions
from typing import Callable
from openai import OpenAI
from openai.types.beta.threads import message

tools = [
  {
      "type": "function",
      "function": {
          "name": "get_weather",
          "parameters": {
              "type": "object",
              "properties": {
                  "location": {"type": "string"}
              },
          },
      },
  }
]


def weather(city : str) -> str:
    """Returns a mock weather report for a given city

    Args:
        city (str): The city to get the weather for

    Returns:
        str: A string containing the current weather
    """

    return f"The current weather in {city} is sunny with a temperature of 70 degrees"





class chat_with_agent:
    def __init__(self,tools : list, messages : list) -> None:
        self._completions = []
        self._messages = messages
        self.client = OpenAI()
        self.tools = tools

    def invoke(self , messages : list) -> str:
        self._messages = messages
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self._messages,
            tools=self.tools,
        )
        self._completions.append(response)
        continue_execution, execution_result = AgentExecutor(self._completions, weather)
        # self._messages.append({"role": "assistant", "content": execution_result})
        ## all the messages role is user,
        # self._messages.append({"role": "user", "content": execution_result})
        self._messages.append({"role": "assistant", "content": f" weather tool output -> {execution_result}"})
        

        if continue_execution == True:
            return self.invoke(self._messages)
        else:
            return self._messages

def AgentExecutor(completions : list, weather : Callable) -> str:

    # check if the the fisish reason is stop in the LLM's last response 
    if completions[-1].choices[0].finish_reason == "stop":
        print("Inside stop reason", {"role": "assistant", "content": completions[-1].choices[0].message.content})
        return (False, completions[-1].choices[0].message.content)
    else:
        ## enter the execution loop
        ### for now we have only one tool
        tool = completions[-1].choices[0].message.tool_calls
        function_name = tool[0].function.name
        args = tool[0].function.arguments
        
        if function_name == "get_weather":
            weather_report = weather(args)
            print("Inside weather tool",{"role": "assistant", "content": f" weather tool output -> {weather_report}"})
            return (True, weather_report)


messages = []
chat = chat_with_agent(tools, messages)
while True:
    inp = input("Enter your message: ")
    if inp == "exit":
        break
    messages.append({"role": "user", "content": inp})
    chat.invoke(messages)



    
