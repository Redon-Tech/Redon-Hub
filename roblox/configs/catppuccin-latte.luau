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
	Background = Color3.fromRGB(239, 241, 245), -- Base
	BackgroundAccent = Color3.fromRGB(230, 233, 239), -- Mantle
	
	Primary = Color3.fromRGB(4, 165, 229), -- Accent: default is sky
	Secondary = Color3.fromRGB(204, 208, 218), -- Surface 0
	Success = Color3.fromRGB(64, 160, 43), -- Green
	Info = Color3.fromRGB(30, 102, 245), -- Blue
	Warning = Color3.fromRGB(223, 142, 29), -- Yellow
	Danger = Color3.fromRGB(210, 15, 57), -- Red
	Light = Color3.fromRGB(156, 160, 176), -- Overlay 0
	Dark = Color3.fromRGB(172, 176, 190), -- Surface 2
	
	TextColor = Color3.fromRGB(76, 79, 105), -- Text
	AccentTextColor = Color3.fromRGB(220, 224, 232), -- Crust
	
	ImageAccentColor = Color3.fromRGB(124, 127, 147), -- Overlay 2
}
-- The colors used by catppuccin are from:  https://github.com/catppuccin/catppuccin

return Settings