---
authors:
    - parker02311
---

This guide is the next part after [setting up the database](/setup/bot/database). If you have not setup the database yet please do so before continuing.

## Creating the JSON File
The bot uses a mix of both a `config.json` and a `.env` file for configuration. The `config.json` file is used for configuration that is not sensitive and can be shared publicly. The `.env` file is used for sensitive information such as tokens and database connection strings. To create the `config.json` file we will copy the `example.config.json` file and rename it to `config.json`. We can do this with the following.

=== "Windows"
    <video width="1920" height="1080" controls>
        <source src="/assets/create_config.mp4" type="video/mp4">
    </video>
=== "Linux"
    ```bash
    cp config.example.json config.json
    ```

## Configuration Explained
Now that we have our `config.json` file we can start configuring it. Below is a list of all the options and what they do.
```json
{
    "Bot": {
        "Prefix": ".",
        "Guilds": [
            1234567890
        ],
        "Owners": [
            1234567890
        ],
        "Activity": {
            "Presence": "watching {users:,} costumers • Version {version}",
            "Status": "online"
        }
    },
    "Logging": {
        "PurchasesChannel": 1234567890,
        "GlobalCustomerRole": 1234567890
    },
    "Data": {
        "Database": "mysql|postgresql|mongodb|"
    },
    "API": {
        "IP": "0.0.0.0",
        "Port": 5000,
        "Key": "CHANGEME"
    }
}
```

- Bot:
    - Prefix: The prefix the bot will use for commands. (Unused)
    - Guilds: A list of guilds the slash commands will be in, please note the first guild in this list will also be the guild the bot will use for customer roles and the purchase channel.
    - Owners: A list of user IDs that will be able to use owner commands.
    - Activity:
        - Presence: The presence the bot will use. Supports the following variables:
            - `{users:,}`: The number of users in the database.
            - `{guilds:,}`: The number of guilds the bot is in.
            - `{version}`: The version of the bot.
            - `{prefix}`: The prefix of the bot.
        - Status: The status the bot will use.
- Logging:
    - PurchasesChannel: The channel ID of the channel the bot will log purchases in.
    - GlobalCustomerRole: The role ID of the role the bot will give to customers of all products.
- Data:
    - Database: The type of database being used. If you are using MariaDB make sure to use `mysql`.
- API:
    - IP: The IP the API will listen on. (Best left as `"0.0.0.0"`)
    - Port: The port the API will listen on. (This port must be open to the internet)
    - Key: The key the API will use for authentication. (This key must be kept secret)


## Finishing the .env file

Now that we have our `config.json` file we can finish our `.env` file. To do this we will add the following to the `.env` file. Replace the values with your own.

```bash
token=this_is_your_bot_token
```

[Next: Starting the Bot](/setup/bot/running){ .md-button .md-button--primary }