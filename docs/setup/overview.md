---
authors:
    - parker02311
---

!!! warning

    The system is in full release, however there may still be bugs due to a lack of testers. Please understand that the system is not perfect and may have bugs. If you find a bug please report it via [GitHub](https://github.com/Redon-Tech/Redon-Hub/issues/new).

# Video Guide
You can watch a video guide on how to setup the system [here](https://youtu.be/LUYU81bWwLY).

??? warning

    This video could become outdated in the future. If you are having issues please refer to the text guide.

# Overview
Redon Hub is designed to be as easy as possible to use. However, it is still a complex system. This guide will walk you through the installation process. If you need assistance you can ask in our Discord server, but please keep in mind this process is not easy and you should only attempt it if you have experience with databases and Discord bots.

# Requirements
- A computer or server to host the system on
    - To be able to recieve Roblox requests you must have a port open
    - It must be online 24/7
    - If you are unable to achieve either of these [we provide a hosting service for a small fee (limited free slots avaliable)](https://billing.redon.tech/)
- Currently you must have either a relational database (MySQL, PostgreSQL, etc.) or MongoDB ready.
- Have a [Discord bot token](https://discord.com/developers/applications) ready.
- [Python](https://www.python.org/downloads/release/python-31010/) 3.9+ installed (With pip)
- [Git](https://git-scm.com/downloads) installed (Optional, faster for setup)

??? abstract "Hosting at home"

    I will not be providing any support with port forwarding, I recommend you use a hosting service. If you are unable to figure out how to use a hosting service [we provide one](https://billing.redon.tech).

[Roblox Setup](roblox/setup.md){ .md-button .md-button--primary }
[Setup Bot](bot/local/setup.md){ .md-button .md-button--primary }
[Setup Bot on Pterodactyl](bot/pterodactyl/setup.md){ .md-button .md-button--primary }