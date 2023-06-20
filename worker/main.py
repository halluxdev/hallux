# Usage example:
# PULL_REQUEST_NUMBER=3 python ./worker/main.py

import os
import openai
from github import Github

print("Hello from worker/main.py")

# Obtain the Github token from the environment and raise an exception if it's not set
github_token = os.getenv("GITHUB_TOKEN")
if github_token is None:
    raise Exception("GITHUB_TOKEN not set")

# Obtain the OpenAI API key from the environment and raise an exception if it's not set
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise Exception("OPENAI_API_KEY not set")
openai.api_key = openai_api_key

# Obtain the pull request number from the environment and raise an exception if it's not set
pull_request_number = os.getenv("PULL_REQUEST_NUMBER")
if pull_request_number is None:
    raise Exception("PULL_REQUEST_NUMBER not set")
print(f"Pull Request Number: {pull_request_number}")


# Create a Github instance using an access token
gh = Github(github_token)

# Then get the repository
repo = gh.get_repo("halluxai/hallux")

pull_request = repo.get_pull(int(pull_request_number))
print(f"Pull Request: {pull_request}")


def make_query():
    openai_model = os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo"
    print(f"Using OpenAI model {openai_model}")

    response = openai.Completion.create(model=openai_model, prompt="Tell it related joke")
    message = response["choices"][0]["text"]
    return message


# Pull request flow
def pull_request_flow():
    print(pull_request.title)
    print(pull_request.user.login)
    print(pull_request.body)
    print(pull_request.state)

    modified_files = pull_request.get_files()

    for file in modified_files:
        print(file.filename)
        print(file.status)
        print(file.patch)

        if file.filename.endswith(".py"):
            print("Python file")
            # print("======")
            # content=repo.get_contents(file.filename)
            # print(content.decoded_content)
            print("======\n\n")

            # Initiate test commit
            if file.filename == "worker/main.py":
                add_pull_request_comment("This line can be improved. Here's a proposed change.", file.filename, 37)


    # print(pull_request.get_files())


def add_pull_request_comment(comment_body, file_path, line_number):
    # Get the file from the pull request
    files = pull_request.get_files()
    target_file = next((file for file in files if file.filename == file_path), None)

    if target_file:
        # Add a comment to the specific line in the file
        commit_id = pull_request.head.sha
        commit = repo.get_commit(commit_id)
        comment = pull_request.create_review_comment(comment_body, commit, target_file.filename, line_number)

        print(f"Comment added on line {line_number} of {target_file.filename}: {comment.html_url}")
    else:
        print(f"File {file_path} not found in the pull request.")

# Usage example
# pull_request_number = 1  # Replace with the actual pull request number
# comment_body = "This line can be improved. Here's a proposed change."
# file_path = "path/to/file.py"  # Replace with the actual file path
# line_number = 42  # Replace with the actual line number

# add_pull_request_comment(pull_request_number, comment_body, file_path, line_number)


# print(make_query())


pull_request_flow()


print("End of worker/main.py")
