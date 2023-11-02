																																																					--[[
  _____               _                     _______                 _     
 |  __ \             | |                   |__   __|               | |    
 | |__) |   ___    __| |   ___    _ __        | |      ___    ___  | |__  
 |  _  /   / _ \  / _  |  / _ \  |  _ \       | |     / _ \  / __| |  _ \ 
 | | \ \  |  __/ | (_| | | (_) | | | | |      | |    |  __/ | (__  | | | |
 |_|  \_\  \___|  \__,_|  \___/  |_| |_|      |_|     \___|  \___| |_| |_|
                                                                 Redon Hub
                                                         Settings
																																																						]]

local Settings = {}

--// Server Communication Configuration \\--
Settings.ServerAddress = "http://x.x.x.x:xxxx/" -- The address to your API
Settings.APIKey = "exampleapikey" -- The API key set in your .env

--// UI Configuration \\--
Settings.BrandName = "Redon Tech" -- The name of the brand to be displayed
Settings.BrandImage = "http://www.roblox.com/asset/?id=13255176500" -- The icon of the brand to be displayed
Settings.AboutUs = [[
Redon Tech Is A Tech Company
You can make new lines by just hitting enter

<b>Supports rich text!</b>
https://create.roblox.com/docs/building-and-visuals/ui/rich-text
]]

Settings.FeaturedProduct = "test" -- The name of the product featured on the home page

Settings.UseCustomColors = false -- Enable custom colors
Settings.Colors = { -- Custom colors
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
-- The colors used by default are from:  https://bootswatch.com/superhero/

return Settings