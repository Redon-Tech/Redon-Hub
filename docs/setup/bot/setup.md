---
authors:
    - parker02311
---

Before we get to setting up our database and configuring the bot we must first install the system. To do this we will use git to clone the repository. If you do not have git installed you can download it [here](https://git-scm.com/downloads).

1. Open a terminal and navigate to the directory you want to install the system in.
2. Download the repository
    - Via Git:
    ```bash
    git clone https://github.com/Redon-Tech/Redon-Hub.git

    # Get the latest release version
    # if you want the latest development version do not run this.
    git checkout $(git describe --tags $(git rev-list --tags --max-count=1))
    ```
    - Via Zipfile:
        1. Download the source code from GitHub.
        2. Extract contents into your install directory.

3. Enter a pipenv
=== "Windows"
    ```bash
    cd Redon-Hub

    python -m pip install pipenv

    python -m pipenv shell
    ```
=== "Linux"
    ```bash
    cd Redon-Hub

    pip install pipenv

    pipenv shell
    ```

4. Install the requirements
=== "Windows"
    ```bash
    python -m pip install -U -r requirements.txt
    ```
=== "Linux"
    ```bash
    pip install -U -r requirements.txt
    ```

[Next: Database Setup](/setup/bot/database){ .md-button .md-button--primary }