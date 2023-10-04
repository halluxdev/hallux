# Configuration

By default Hallux requires a minimal configuration which can be set in enverionment variables and a `.hallux` file.


## Environment Variables

In addition to the YAML configuration file, Hallux also supports configuring options via environment variables. This allows overriding configuration values without modifying the file and keeping secrets out of version control.

### Backends
 * **OPENAI_API_KEY** - API key for OpenAI APIs like GPT-3

 * **AZURE_OPENAI_API_KEY** - API key for Azure OpenAI APIs
 * **AZURE_OPENAI_ENDPOINT** - Endpoint for Azure OpenAI APIs

### Tools
 * **SONARQUBE_TOKEN** - Token for authenticating with SonarQube server


## Configuration file

Hallux looks for a `.hallux` configuration file in the current or parent directories. This file is in YAML format and allows configuring Hallux behavior.


### Example Configuration

Here is an example `.hallux` file:

```yaml
target: files

backends:
  - cache: cache.json
  - gpt3:
      model: gpt-3.5-turbo

tools:
  python:
    ruff: true
  sonar:
    url: https://sonar.mycompany.com
```

This will:

 * Apply fixes directly to files (default)
 * First check a local cache cache.json
 * Then fallback to GPT-3.5 if cache misses
 * Run Ruff for Python linting
 * Run compilation for C++
 * Get SonarQube issues using the configured URL and SONAR_TOKEN
 * Configuration Options
 * The main sections are:

#### target

The target specifies where fixes will be applied:

- **files**: Directly modify files in place (default)
- **git**: Apply fixes to files + individual git commits
- **github**: Open PR with fixup commits against a GitHub PR URL

#### backends

The backends list specifies the order to query backends:

- **cache**: Check a local JSON cache file first
- **gpt3**: Query OpenAI's GPT-3
- **gpt4**: Query OpenAI's GPT-4

Each backend can be configured with additional options like model and max_tokens.

#### tools

The tools section specifies which tools to run by language:

- **python**: Configure Python tools like ruff
- **cpp**: Configure C++ tools like compile
- **sonar**: Configure SonarQube integration

Each tool has additional configuration options.



Complete confiugration options:

```yaml
target: files # | git | github
backends:
    - cache: # short-name, used in command-line
        type: dummy # type : dummy / openai / hallux
        filename: dummy.json

    - rest:
        type: rest
        url: http://localhost:8000/generate
        request_body: { message: $PROMPT } # Defaults to: $PROMPT
        response_body: $RESPONSE.answer # Defaults to $RESPONSE

    - gpt3:
        type: openai
        model: gpt-3.5-turbo
        max_tokens: 4096

    - gpt3azure:
        type: openai.azure
        model: gpt-3.5-turbo
        max_tokens: 4096

    - gpt3-long:
        type: openai
        model: gpt-3.5-turbo-16k
        max_tokens: 16384

    - gpt4:
        type: openai
        model: gpt-4
        max_tokens: 8192

    - gpt4-long:
        type: openai
        model: gpt-4-32k
        max_tokens: 32768

tools:
    ruff:
        # command-line arguments for ruff
        args:
    mypy:
        # command-line arguments for mypy
        args: --ignore-missing-imports
    sonar:
        url: https://sonarqube.hallux.dev
        success_test: ./hallux-test.sh -x
        project: halluxdev_hallux_AYpIk3Z__hwOMJbIE7XQ
    cpp:


groups:
    all: ["ruff", "mypy", "sonar", "cpp"]
    python: ["ruff", "mypy"]


```