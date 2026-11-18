# Personal Budget 

## Idea
Creating a local budget visualizer. Powered by Python and LLMs. 

Input - Monthly spending CSVs from Capital One

Output - Properly formatted spending summary month by month

## Checkpoints

0. CSVs with transaction info in and setup project infrastructure
**We are here**
1. Python parses input
2. LLM cleans fuzzy input
3. LLM categorizes transactions
4. Python verifies LLM work
5. Python visualizes

### 0. CSVs with transaction info in

Downloaded manually from Capital One portal per statement. See: "budget/data"

---

At this stage, I have prepped for checkpoint 1 work. I localized qwen3:14b and am using that - thinking mode is good, still get good results without it. Still need to think big picture and prep folder/file architecture. Then set up the logistics - I want code in this project containerized. 

Container 2 (Dev Container) is built from a Dockerfile and requirements.txt (Python/SQL libraries) in this repo, bridged into Zed via .devcontainer/devcontainer.json with host networking so your code, terminal, and AI agent execute inside Docker while .gitignore excludes local datasets, caches, and .env secrets from Git.

budget/
├── data/
│   └── capital_one.csv
├── src/
│   ├── clean_input.py
│   ├── categorize.py
│   └── visualize.py
├── Dockerfile
├── requirements.txt
└── .devcontainer/
    └── devcontainer.json

I ran `docker exec -it ollama-global bash` to jump into my LLM container and then `ollama pull qwen3:14b` to download qwen3. I can remove any model by running `ollama rm <model-name>` in the LLM container.

Need to refresh Zed to make sure it picks up the model after adding, click into AI window on left, press Ctrl+Alt+C, "LLM Providers" -> Configure, scroll down to "Ollama" -> Configure, click refresh where it says "Connected" on bottom right.

---

### [Superseded by [Dev Container Infrastructure](#dev-container-infrastructure)] Development Infrastructure

Working now to setup the infrastructure for development - Docker dev container and hooking up into Zed.
Going to start by building a slim python docker container with a Dockerfile.
Then will connect it to Zed.

Holy moly, difficult.
Took a bit to get set up properly.
Now using a docker-compose.yml file to coordinate the docker stuff, lays foundation for future database/frontend container connections. 
Building through Zed creates a custom image off of the defined `budget-app` image tag and creates an app-dev container called `budget-app-dev`.
When any changes are made to the Dockerfile, you must clear out the container and image so it can be rebuilt properly:

`docker stop budget-app-dev
docker rm budget-app-dev
docker rmi budget-<hashID>-features:latest`

When using Zed, the container will live even after closing the IDE.
The container will start on PC reboot as well.
Zed will save recent projects, open by clicking on the project name in the top left or File > Open Remote > Connect Dev Container.

If needed, you can manually start the container from the .devcontainer info with Ctrl+Shift+P to open the Command Pallete and run "Open dev container". 

----

### Git Integration

Next step should be to get a git repo going. 

Set up SSH auth to git account on local at ~/.ssh and with ~/.gitconfig.
Looking to passthrough SSH_AUTH_SOCK (ssh agent) to the container to handle authentications.
Currently doing through docker-compose.override.yml.

Agent passthrough success, docker container recreated properly.
Git is authenticating properly to github.com.
Noticing now that the Docker container runs with the `root` user.
This can cause file permission errors on the bind mount.
Cleaner to give Docker its own user.
Dev container now set up with its own user `devuser`.
Git auth passthrough working as expected.
Ready to git init in container.

Git repo created at `https://github.com/fchiave/personal-budget`. 

---

### Dev Container Infrastructure

Running into container issues on start up.
Now manually managing container state instead, this cleans up the containerization approach as a whole.

Makefile created to simplify commands as container names vary per build.
Container state now handled through `make` commands: `make up`, `make down`, `make status`, `make clean`.
Stop container when done working with `make down`, start container to begin work with `make up`, check container status with `make status`.

When fundamental container changes are made, a new image and container need to be built.
Tear down with `make clean` and use Zed's Command Palette (Ctrl+Shift+P) to run "projects: open dev container". 

---

Will want to add testing and linting integration.
Potentially basic CI/CD

For future CI/CD work, look to split Dockerfile into a multi-stage build for GitHub actions (base -> dev -> prod).

---

### 1. LLM parses and cleans input
