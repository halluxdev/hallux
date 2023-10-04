# SonarQube Integration

In order to retrieve issues from SonarQube and generate corresponding fix proposals, Hallux needs to connect to a SonarQube server.

The configuration can be done with environment variables or in the `.hallux` configuration file as following:


```yaml
tools:
    sonar:
        url: [SONAR_URL]
        success_test: [SONAR_SUCCESS_TEST]
        project: [SONAR_PROJECT_KEY]
```

* `SONAR_TOKEN` - can only be added as environment variable with value of your SonarQube token


* `SONAR_SUCCESS_TEST` is used to verify that the fix was applied successfully. For example, you can run unit test to make sure nothing broke: `"pytest tests/test_file.py"`