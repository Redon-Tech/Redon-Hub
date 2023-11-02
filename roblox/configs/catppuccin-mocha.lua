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

Settings.UseCustomColors = true -- Enable custom colors
Settings.Colors = { -- Custom colors
	Background = Color3.fromRGB(30, 30, 46), -- Base
	BackgroundAccent = Color3.fromRGB(24, 24, 37), -- Mantle
	
	Primary = Color3.fromRGB(137, 220, 235), -- Accent: default is sky
	Secondary = Color3.fromRGB(49, 50, 68), -- Surface 0
	Success = Color3.fromRGB(166, 227, 161), -- Green
	Info = Color3.fromRGB(137, 180, 250), -- Blue
	Warning = Color3.fromRGB(249, 226, 175), -- Yellow
	Danger = Color3.fromRGB(243, 139, 168), -- Red
	Light = Color3.fromRGB(108, 112, 134), -- Overlay 0
	Dark = Color3.fromRGB(88, 91, 112), -- Surface 2
	
	TextColor = Color3.fromRGB(205, 214, 244), -- Text
	AccentTextColor = Color3.fromRGB(17, 17, 27), -- Crust
	
	ImageAccentColor = Color3.fromRGB(147, 153, 178), -- Overlay 2
}
-- The colors used by catppuccin are from:  https://github.com/catppuccin/catppuccin

return Settings