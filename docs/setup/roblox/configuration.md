---
authors:
    - parker02311
---

This guide is the next part after [setting up the place](/setup/roblox/setup). If you have not setup a place yet please do so before continuing.

## Finding the Configuration module
The configuration file is located in ServerScriptService under the name `Configuration`. You can find it by searching for it in the explorer.

## Configuration Explained
Now that we have our configuration module we can start configuring it. Below is a list of all the options and what they do.
```lua
--// Server Communication Configuration \\--
Settings.ServerAddress = "http://x.x.x.x:xxxx/"
Settings.APIKey = "exampleapikey"

--// UI Configuration \\--
Settings.BrandName = "Redon Tech"
Settings.BrandImage = "http://www.roblox.com/asset/?id=13255176500"
Settings.AboutUs = [[
Redon Tech Is A Tech Company
You can make new lines by just hitting enter

<b>Supports rich text!</b>
https://create.roblox.com/docs/building-and-visuals/ui/rich-text
]]

Settings.FeaturedProduct = "test"

Settings.UseCustomColors = false
Settings.Colors = {
	Background = Color3.fromRGB(15, 37, 55),
	BackgroundAccent = Color3.fromRGB(32, 55, 76),
	
	Primary = Color3.fromRGB(65, 132, 197),
	Secondary = Color3.fromRGB(66, 79, 92),
	Success = Color3.fromRGB(78, 156, 78),
	Info = Color3.fromRGB(77, 163, 189),
	Warning = Color3.fromRGB(217, 164, 6),
	Danger = Color3.fromRGB(184, 71, 67),
	Light = Color3.fromRGB(145, 155, 165),
	Dark = Color3.fromRGB(32, 55, 76),
	
	TextColor = Color3.fromRGB(255, 255, 255),
	AccentTextColor = Color3.fromRGB(0, 0, 0),
	
	ImageAccentColor = Color3.fromRGB(148, 166, 180),
}
```

- ServerAddress: The address of the server. This is usually the IP address of the server. Must start with `http` or `https`
- APIKey: The API key of the server. This is used to authenticate requests to the server. You can find this in the `config.json` file of the bot.
- BrandName: The name of the brand. This is displayed in the top left of the UI.
- BrandImage: The image of the brand. This is displayed in the top left of the UI. Must be `rbxassetid://` or `http://www.roblox.com/asset/?id=`.
- AboutUs: A multi-line string that is displayed on the about us page. Supports [rich text](https://create.roblox.com/docs/building-and-visuals/ui/rich-text).
- FeaturedProduct: The product name of the featured product. This is displayed on the home page.

Custom Colors:

- UseCustomColors: Whether or not to use custom colors. If this is set to false the colors will be set to the default theme colors.
- Colors:
    - All of these are pretty self explanatory. They are the colors used in the UI. You can use [this tool](https://www.w3schools.com/colors/colors_picker.asp) to find the RGB values of colors.