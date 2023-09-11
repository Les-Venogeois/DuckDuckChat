import openai, json
from typing import List, Dict, Optional
from tenacity import retry, wait_random_exponential, stop_after_attempt
import functions

class ChatBot():
    def __init__(self, API_KEY: str, functions: List[Dict] = None, model: str = "gpt-3.5-turbo-0613") -> None:
        """Initialize the ChatBot
        
        Args:
            API_KEY (str): OpenAI API Key
            functions (List[Dict], optional): List of functions availible for the AI to use. Defaults to None.
            model (str, optional): Model to use. Defaults to "gpt-3.5-turbo-0613".
        """
        openai.api_key = API_KEY
        self.functions: Optional[List[Dict]] = functions
        self.model: str = model
        self.system_message = """You are a helpful AI-powered search engine and assistant called DuckDuckChat. You can help users with a variety of tasks.
Introduce yourself to the user at the beggining of your first message. Eg: "Hi! I'm DuckDuckChat!".
Your main goal is to search the web for answers to the user's questions.
Use the "search" function to search the web for answers to the user's questions. Then parse the results and return them to the user with a natural language response that summurizes the results.
Your output should be markdown formatted. Cite your sources using markdown links. Eg: "... According to [Microsoft](https://microsoft.com), Office365...".
You can also do everything that GPT-3 can do like writing stories, poems, and code.
Never use your internal knowledge to answer questions. Always use the internet.
When you search the web via the "search" function, you must call it minimum once, and maximum 3 times. If you can't find an answer after 3 tries, you must tell the user that you can't find an answer.
"""
        self.messages: List[Dict] = [{"role": "system", "content": self.system_message}]

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_request(self, function_call: str=None) -> str:
        """Send a request to the OpenAI Chat API

        Args:
            function_call (str, optional): Force the AI to use that specific function. Defaults to None.

        Returns:
            str: Response from the API
        """        
        try:
            if function_call:
                completion = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.messages,
                    functions=self.functions,
                    function_call=function_call
                )
            else:
                completion = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.messages,
                    functions=self.functions
                )
            result = completion.choices[0].message
            # if result.content is not None and getattr(result, 'function_call', None) is not None:
            #     print(f"Bot: {result.content}")
            #     return str(result)
            if result.content:  # Removed elif
                return result.content
            else:
                return str(result)
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return str(e)
        
    def user_chat(self, message: str):
        return self.chat({"role": "user", "content": message})

    def chat(self, message: Dict):
        """Send a message to the AI

        Args:
            message (str): Message to send to the AI

        Returns:
            str: Response from the AI
        """        
        self.messages.append(message)
        result = self.chat_request()
        self.messages.append({"role": "assistant", "content": result})
        try:
            parsed_result = json.loads(result)
            if parsed_result["function_call"]:
                try:
                    func_return = self.execute_function(parsed_result["function_call"]["name"], json.loads(parsed_result["function_call"]["arguments"]))
                    return self.chat({"role": "function", "name": parsed_result["function_call"]["name"], "content": func_return})
                except Exception as e:
                    print(f"Unable to execute function: {e}")
                    return self.chat({"role": "function", "name": parsed_result["function_call"]["name"], "content": str(e)})
            else:
                return result
        except json.JSONDecodeError: # That means that the result is not a function call (because it's not JSON)
            return result
        except Exception as e:
            print(f"Unable to parse result: {e}")
            return result
        
    # Deprecated
    def clear_conversation(self) -> None:
        """Clear the conversation history"""        
        self.messages = [{"role": "system", "content": self.system_message}]

    def execute_function(self, function_name: str, arguments: List[str]) -> str:
        """Execute a function

        Args:
            function_name (str): Name of the function to execute
            arguments (List[str]): Arguments to pass to the function

        Returns:
            str: Response from the API
        """        
        try:
            if function_name == "exit_conversation":
                self.exit_conversation()
            result = eval(f"functions.{function_name}({arguments})")
            return result
        except Exception as e:
            print("Unable to execute function")
            print(f"Exception: {e}")
            return str(e)
        
    def exit_conversation(self) -> None:
        """Exit the conversation"""     
        # Save conversation history to a formatted json file
        from datetime import datetime
        import os

        day = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H-%M-%S")

        if not os.path.exists("conversations"):
            os.mkdir("conversations")
        if not os.path.exists(f"conversations/{day}"):
            os.mkdir(f"conversations/{day}")

        messages = self.messages
        messages.insert(0, {"functions": functions.list})
        messages.append({"role": "system", "content": "Conversation ended."})

        with open(f"conversations/{day}/{time}.json", "w") as f:
            json.dump(messages, f, indent=4)
        exit()
    

if __name__ == "__main__":
    # Warning: "gpt-4-0613" costs a lot compared to "gpt-3.5-turbo-0613"
    # Default model: "gpt-3.5-turbo-0613"
    models = ["gpt-3.5-turbo-0613", "gpt-4-0613"]
    from os import getenv
    API_KEY = getenv("OPENAI_API_KEY")
    bot = ChatBot(API_KEY, functions.list, models[0])
    while True:
        try:
            message = input("You: ")
            print(f"Bot: {bot.user_chat(message)}")
        except KeyboardInterrupt:
            bot.exit_conversation()