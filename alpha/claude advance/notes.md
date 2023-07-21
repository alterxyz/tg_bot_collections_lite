# notes

## dependencies

venv: python3.10

### Anthropic

```bash
pip install anthropic
```

### Vertext AI (Windows tested)

```bash
pip install -U google-cloud-aiplatform "anthropic[vertex]"
gcloud init
gcloud info # check if it's correct
# then you should login with your browser, choose the project, and set the region
# then you many wanna restart the terminal / Windows system
# Try: gcloud info in raw terminal, if pass, then:
gcloud auth application-default login
```
