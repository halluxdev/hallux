import os

print("Hello from worker/main.py")

github_token = os.getenv('GITHUB_TOKEN')

if github_token is None:
    raise Exception('GITHUB_TOKEN not set')

openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key is None:
    raise Exception('OPENAI_API_KEY not set')

print("End of worker/main.py")