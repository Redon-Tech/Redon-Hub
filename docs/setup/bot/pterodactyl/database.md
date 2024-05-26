---
authors:
    - parker02311
---

This guide is the next part after [installing the system](setup.md). If you have not installed the system yet please do so before continuing.

!!! warning

    The Pterodactyl egg is designed for MySQL (MariaDB) only. If you are using a different database the hosting provider will need to modify your egg.

### Connection String
After you have choosen the database type you are going to use, make the connector string and save it for later. You will need it in the next step. [Get help with connection strings](https://www.prisma.io/docs/reference/database-reference/connection-urls)

??? example

    ```
    mysql://USER:PASSWORD@HOST:PORT/DATABASE
    ```

## Setting Up ENV Variables
Now that we have our database setup we need to configure the bot to use it. To do this we will use a .env file. This file will contain all of our environment variables that the bot will use. To create the .env file we can do the following.
<video width="1920" height="1080" controls>
    <source src="/assets/create_pterodactyl_env.mp4" type="video/mp4">
</video>

Replace the values with your own.

## Using Prisma
We use [Prisma](https://www.prisma.io/) to manage our database. To setup Prisma we will do the following.

1. Click the "Startup" tab.
2. Enable "DB Push".

[Next: Configuration](configuration.md){ .md-button .md-button--primary }