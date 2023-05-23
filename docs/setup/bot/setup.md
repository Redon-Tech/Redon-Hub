---
authors:
    - parker02311
---

# Installation
Before we get to setting up our database and configuring the bot we must first install the system. To do this we will use git to clone the repository. If you do not have git installed you can download it [here](https://git-scm.com/downloads).

1. Open a terminal and navigate to the directory you want to install the system in.
2. Clone the repository
    Via Git:
    ```bash
    git clone https://github.com/Redon-Tech/Redon-Hub.git

    # Get the latest release version
    # if you want the latest development version do not run this.
    git checkout $(git describe --tags $(git rev-list --tags --max-count=1))
    ```
3. Enter a pipenv
    ```bash
    cd Redon-Hub

    pip install pipenv

    pipenv shell
    ```
4. Install the requirements
    ```bash
    pip install -U -r requirements.txt
    ```