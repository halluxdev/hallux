import os
import openai
from github import Github

print("Hello from worker/main.py")

github_token = os.getenv("GITHUB_TOKEN")

if github_token is None:
    raise Exception("GITHUB_TOKEN not set")

openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise Exception("OPENAI_API_KEY not set")
openai.api_key = openai_api_key


pull_request_number = os.getenv("PULL_REQUEST_NUMBER")


def make_query():
    openai_model = os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo"
    print(f"Using OpenAI model {openai_model}")

    response = openai.Completion.create(model=openai_model, prompt="Tell it related joke")
    message = response["choices"][0]["text"]
    return message


# Pull request flow


def pull_request_flow(pull_request_number):
    # First create a Github instance using an access token
    g = Github(github_token)

    # Then get the repository
    repo = g.get_repo("halluxai/hallux")

    # Then get the pull request
    # Replace 1 with the number of the pull request you want to get
    # pull_request = repo.get_pull(1)

    # Now you can get details about the pull request

    print(f"Pull Request Number: {pull_request_number}")

    pull_request = repo.get_pull(int(pull_request_number))
    print(f"Pull Request: {pull_request}")

    print(pull_request.title)
    print(pull_request.user.login)
    print(pull_request.body)
    # print(pull_request)
    modified_files = pull_request.get_files()
    # print(modified_files)
    for file in modified_files:
        print(file.filename)
        print(file.patch)
        print("======\n\n")

    # print(pull_request.get_files())


# print(make_query())

if pull_request_number is not None:
    pull_request_flow(pull_request_number)


print("End of worker/main.py")
