import os
import openai

print("Hello from worker/main.py")

github_token = os.getenv("GITHUB_TOKEN")

if github_token is None:
    raise Exception("GITHUB_TOKEN not set")

openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise Exception("OPENAI_API_KEY not set")


openai_model = os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo"
print(f"Using OpenAI model {openai_model}")


# Step 1, send model the user query and what functions it has access to
def make_query():
    response = openai.Completion.create(model=openai_model, prompt="Tell it related joke")
    message = response["choices"][0]["text"]
    return message


openai.api_key = openai_api_key


print(make_query())

print("End of worker/main.py")
