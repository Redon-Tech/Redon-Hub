---
authors:
    - parker02311
---

This guide is the next part after [installing the system](/setup/bot/setup). If you have not installed the system yet please do so before continuing.

!!! warning

    The bot was developed and tested on MariaDB (MySQL) and in our current state of development we have not tested any other databases yet. If you have any issues with other databases please let us know in our Discord server. [Details on supported databases.](https://www.prisma.io/docs/reference/database-reference/supported-databases)

### Connection String
After you have choosen the database type you are going to use, make the connector string and save it for later. You will need it in the next step. [Get help with connection strings](https://www.prisma.io/docs/reference/database-reference/connection-urls)

??? example

    ```
    mysql://USER:PASSWORD@HOST:PORT/DATABASE
    ```

## Setting Up ENV Variables
Now that we have our database setup we need to configure the bot to use it. To do this we will use a .env file. This file will contain all of our environment variables that the bot will use. To create the .env file we can do the following.
=== "Windows"
    <video width="1920" height="1080" controls>
        <source src="/assets/create_env.mp4" type="video/mp4">
    </video>
=== "Linux"
    ```bash
    touch .env
    ```

Now we will add the following to the .env file. Replace the values with your own.
```bash
token=we_will_come_back_to_this_later
database=mysql://USER:PASSWORD@HOST:PORT/DATABASE
```

## Using Prisma
We use [Prisma](https://www.prisma.io/) to manage our database. To setup Prisma we will use the following command.

=== "Relational Database"
    - Windows
    ```bash
    python -m prisma generate --schema relational-schema.prisma

    # Using db push is not always the best way to do this, however it is the easiest.
    python -m prisma db push --schema relational-schema.prisma
    ```
    - Linux
    ```bash
    python3 -m prisma generate --schema relational-schema.prisma

    # Using db push is not always the best way to do this, however it is the easiest.
    python3 -m prisma db push --schema relational-schema.prisma
    ```

=== "MySQL (MariaDB)"
    - Windows
    ```bash
    python -m prisma generate --schema mysql-schema.prisma

    # Using db push is not always the best way to do this, however it is the easiest.
    python -m prisma db push --schema mysql-schema.prisma
    ```
    - Linux
    ```bash
    python3 -m prisma generate --schema mysql-schema.prisma

    # Using db push is not always the best way to do this, however it is the easiest.
    python3 -m prisma db push --schema mysql-schema.prisma
    ```
=== "MongoDB"
    - Windows
    ```bash
    python -m prisma generate --schema mongodb-schema.prisma

    # Using db push is not always the best way to do this, however it is the easiest.
    python -m prisma db push --schema mongodb-schema.prisma
    ```
    - Linux
    ```bash
    python3 -m prisma generate --schema mongodb-schema.prisma

    # Using db push is not always the best way to do this, however it is the easiest.
    python3 -m prisma db push --schema mongodb-schema.prisma
    ```
[Next: Configuration](/setup/bot/configuration){ .md-button .md-button--primary }