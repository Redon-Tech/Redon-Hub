--- 
authors:
    - parker02311
---

This guide is the next part after [configuration](configuration.md). If you have not configured the bot yet please do so before continuing.

## Inviting the Bot
Before we can run the bot we need to invite it to our guild. To do this we will do the following:
<video width="1920" height="1080" controls>
    <source src="/assets/invite_bot.mp4" type="video/mp4">
</video>

Scopes Required: 

- `applications.commands`: This is required for the bot to create slash commands.
- `bot`: This is required for the bot to join the guild.

Permissions Required: 

- `Administrator`: This is the easiest way to ensure the bot has all the permissions it needs.

!!! warning "Ensure Proper Permissions and Scopes"

    If you do not give the bot proper permissions or scopes, commands may not work correctly or not even appear.

??? warning "Warning about Administrator Permissions"

    Giving the bot administrator permissions is not recommended. If you do, please ensure to not leak the token.

## Running the Bot
The easiest part of this entire guide, running the bot. To run the bot we will do the following:

1. Click the "Console" tab.
2. Click "Start" to start the bot.
3. After the bot has started go back to the "Startup" tab.
4. Disable "DB Push".

## Next Steps
Now that you have the bot running you can start using it. If you need help with commands see [commands guide](../../../guide/commands.md) to get a list of commands. If you need help with anything else you can ask in our [Discord](https://discord.gg/Eb384Xw) server.