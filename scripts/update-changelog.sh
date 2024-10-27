#!/bin/bash

# Check if at least one argument is passed
if [ $# -eq 0 ]; then
    echo "Usage: $0 <commit-hash | commit-range>"
    exit 1
fi

# Get the commit hash or range from the first argument
commit_range=$1

# Check if it's a single commit hash or a range
if [[ "$commit_range" =~ \.\. ]]; then
    # It's a commit range
    commit_message=$(git --no-pager log --format=%B "$commit_range")
    diff_output=$(git --no-pager diff "$commit_range")
else
    # It's a single commit
    commit_message=$(git --no-pager log -1 --format=%B "$commit_range")
    diff_output=$(git --no-pager show "$commit_range" --format="")
fi

# Relies on the git tag
MAJOR=$(git describe --long | awk -F "-" '{print $1}')
DISTANCE=$(git describe --long | awk -F "-" '{print $2}')
VERSION=${MAJOR}.${DISTANCE}

# Generate changelog prompt and save it to a variable
changelog_prompt=$(cat <<EOF
For the following commit message and diff, create a changelog record.

## Changelog Format
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning. Remove unused sections.

## Example Changelog Entry:

\`\`\`markdown
### Added

- #123: Add new feature

### Changed

### Deprecated

### Removed

### Fixed
\`\`\`

## Commit Messages

$commit_message

## Diff
\`\`\`diff
$diff_output
\`\`\`
EOF
)

# Properly escape the newlines and quotes for the JSON request
json_payload=$(jq -n --arg prompt "$changelog_prompt" '{
  model: "llama3.2",
  prompt: $prompt,
  stream: false
}')

# Send changelog prompt to LLM API via curl
curl_output=$(curl -s http://localhost:11434/api/generate -H "Content-Type: application/json" -d "$json_payload")

# Extract the 'response' field from the LLM response using jq
formatted_response=$(echo "$curl_output" | jq -r '.response')

# Insert the formatted response into CHANGELOG.md before the latest tag
if [ -f "CHANGELOG.md" ]; then
    # Create a backup of the current CHANGELOG.md
    cp CHANGELOG.md CHANGELOG.md.bak

    # Find the line number of the latest tag and insert before it
    latest_tag_line=$(grep -n "^## \[\d" CHANGELOG.md | head -n 1 | cut -d: -f1)
    
    if [ -z "$latest_tag_line" ]; then
        # No existing tags found, append to the end of the file
        echo "## [$VERSION] - $(date +%Y-%m-%d)" >> CHANGELOG.md
        echo "$formatted_response" >> CHANGELOG.md
        echo "" >> CHANGELOG.md
    else
        # Insert changelog entry before the latest tag
        (head -n $(($latest_tag_line - 1)) CHANGELOG.md; \
         echo "## [$VERSION] - $(date +%Y-%m-%d)"; \
         echo "$formatted_response"; \
         echo ""; \
         tail -n +$latest_tag_line CHANGELOG.md) > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
    fi
    rm -rf CHANGELOG.md.bak
else
    # If no CHANGELOG.md exists, create one
    echo "## [$VERSION] - $(date +%Y-%m-%d)" > CHANGELOG.md
    echo "$formatted_response" >> CHANGELOG.md
fi

echo "Changelog has been updated in CHANGELOG.md."
