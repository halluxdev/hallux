# VS Code

## Debugging with VS Code

Creaate a `launch.json` file in the `.vscode` folder with the following configuration to debug Hallux using VS Code's integrated terminal:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Hallux",
      "type": "python",
      "request": "launch",
      "console": "integratedTerminal",
      "program": "${workspaceFolder}/hallux/main.py",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}:$PYTHONPATH",
      },
      "args" : ["--verbose", "--sonar", "--gpt3", "."]
    }
  ]
}
```
