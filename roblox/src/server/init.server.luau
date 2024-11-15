--[[
	File: ServerScriptService/Hub_Server
	Usage: The hub server.
	Do not edit unless you know what you are doing.
]]

-- Types

type user = {
	id: number,
	createdAt: DateTime,
	discordId: number,
	verifiedAt: DateTime,
	purchases: { number },
}

type tag = {
	id: number,
	name: string,
	color: Color3,
	textColor: Color3,
}

type product = {
	id: number,
	createdAt: DateTime,
	name: string,
	description: string,
	imageId: string,
	price: number,
	productId: number,
	stock: number?,
	tags: { number },
	purchases: number,
	owners: number,
}

-- Variables
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")
local SoundService = game:GetService("SoundService")
local RemoteEvent = ReplicatedStorage:WaitForChild("RemoteEvent")
local RemoteFunction = ReplicatedStorage:WaitForChild("RemoteFunction")
local PlayerReady = ReplicatedStorage:WaitForChild("PlayerReady")

local devMode = SoundService:GetAttribute("DevModeEnabled")
local configuration = require(script.Parent.Configuration)
local serverUrl: string
do
	if devMode then
		serverUrl = SoundService:GetAttribute("DevModeConnection")
	else
		serverUrl = configuration.ServerAddress
	end
end
local apiKey
do
	if devMode then
		apiKey = SoundService:GetAttribute("DevModeKey")
	else
		apiKey = configuration.APIKey
	end
end

local functions = {}
local events = {}
local products: { [number]: product } = {}
local productsByProduct: { [number]: product } = {}
--local users: {[number]:user} = {}
local tags: { [number]: tag } = {}
local serverIsOnline = nil
local cartEnabled = nil

-- Functions

HttpService:GetAsync("https://google.com/robots.txt")

local function isServerOnline()
	local success, data = pcall(function()
		return HttpService:GetAsync(serverUrl, true)
	end)

	if success then
		data = HttpService:JSONDecode(data)
		if data["message"] == "Online" and data["databaseConnected"] == true then
			serverIsOnline = true
			return true
		end
	end

	serverIsOnline = false
	return false
end

local function isCartEnabled()
	local success, data = pcall(function()
		return HttpService:GetAsync(`{serverUrl}v1/cart_enabled`, true, { Authorization = `Bearer {apiKey}` })
	end)

	if success then
		data = HttpService:JSONDecode(data)
		cartEnabled = data
		return cartEnabled
		--print(cartEnabled)
	end

	cartEnabled = false
	return false
end

local function cacheProduct(productInfoRaw)
	if products[productInfoRaw.id] then
		return products[productInfoRaw.id]
	end
	local productInfo: product = {
		id = productInfoRaw.id,
		createdAt = DateTime.fromIsoDate(productInfoRaw.createdAt),
		name = productInfoRaw.name,
		description = productInfoRaw.description,
		imageId = productInfoRaw.imageId,
		price = productInfoRaw.price,
		productId = productInfoRaw.productId,
		stock = productInfoRaw.stock,
		tags = productInfoRaw.tags,
		purchases = productInfoRaw.purchases,
		owners = productInfoRaw.owners,
	}
	pcall(function()
		local marketProductInfo = MarketplaceService:GetProductInfo(productInfo.productId, Enum.InfoType.Product)
		if marketProductInfo then
			if productInfo.price ~= marketProductInfo.PriceInRobux then
				productInfo.price = marketProductInfo.PriceInRobux
			end
		end
	end)

	--print(`product: {productInfoRaw.id}`, productInfo)
	products[productInfoRaw.id] = productInfo
	productsByProduct[productInfoRaw.productId] = productInfo

	return productInfo
end

local function getProducts()
	if serverIsOnline == false then
		return
	end

	local success, data = pcall(function()
		return HttpService:GetAsync(`{serverUrl}v1/products`, nil, { Authorization = `Bearer {apiKey}` })
	end)

	if success then
		data = HttpService:JSONDecode(data)
		for _, productData in pairs(data) do
			cacheProduct(productData)
		end
		return true, products
	else
		print(`getProducts failed because {data}`, "\n", debug.traceback())
		error(data)
	end
end

local function cacheTag(tagInfoRaw)
	if tags[tagInfoRaw.id] then
		return tags[tagInfoRaw.id]
	end
	local tagInfo: tag = {
		id = tagInfoRaw.id,
		name = tagInfoRaw.name,
		color = Color3.fromRGB(tagInfoRaw.color[1], tagInfoRaw.color[2], tagInfoRaw.color[3]),
		textColor = Color3.fromRGB(tagInfoRaw.textColor[1], tagInfoRaw.textColor[2], tagInfoRaw.textColor[3]),
	}

	--print(`tag: {tagInfoRaw.id}`, tagInfo)
	tags[tagInfoRaw.id] = tagInfo

	return tagInfo
end

local function getTags()
	if serverIsOnline == false then
		return
	end

	local success, data = pcall(function()
		return HttpService:GetAsync(`{serverUrl}v1/tags`, nil, { Authorization = `Bearer {apiKey}` })
	end)

	if success then
		data = HttpService:JSONDecode(data)
		for _, tagData in pairs(data) do
			cacheTag(tagData)
		end
		return true, tags
	else
		warn(`getTags failed because {data}`, "\n", debug.traceback())
	end
	return false
end

-- Initial Server Setup
isServerOnline()
isCartEnabled()
getProducts()
getTags()

MarketplaceService.ProcessReceipt = function(receiptInfo)
	--print(receiptInfo)
	if productsByProduct[receiptInfo.ProductId] then
		local productInfo: product = productsByProduct[receiptInfo.ProductId]
		--print(productInfo)

		local success, data = pcall(function()
			return HttpService:GetAsync(`{serverUrl}v1/users/{receiptInfo.PlayerId}/owns/{productInfo.id}`, nil)
		end)

		if success then
			data = HttpService:JSONDecode(data)
			--print(data)
			if data == true then
				return Enum.ProductPurchaseDecision.NotProcessedYet
			end
		else
			return Enum.ProductPurchaseDecision.NotProcessedYet
		end

		success, data = pcall(function()
			return HttpService:RequestAsync({
				Url = `{serverUrl}v1/users/{receiptInfo.PlayerId}/{productInfo.id}?isPurchase=true`,
				Method = "POST",
				Headers = { Authorization = `Bearer {apiKey}` },
			})
		end)
		--print(success, data)
		if success then
			return Enum.ProductPurchaseDecision.PurchaseGranted
		end
	end

	return Enum.ProductPurchaseDecision.NotProcessedYet
end

functions.getUIConfiguration = function()
	local configCopy = table.clone(configuration)
	configCopy.APIKey = nil
	configCopy.ServerAddress = nil
	configCopy.cartEnabled = cartEnabled

	return configCopy
end

functions.isVerified = function(player: Player)
	if serverIsOnline == false then
		return
	end

	local success, data = pcall(function()
		return HttpService:RequestAsync({
			Url = `{serverUrl}v1/users/{player.UserId}/verify/key`,
			Method = "POST",
			Headers = { Authorization = `Bearer {apiKey}` },
		})
	end)

	if success then
		data = HttpService:JSONDecode(data.Body)
		if data["message"] == "User Already Verified" then
			return true
		elseif data["message"] == "Verification Key Created" then
			return data["data"]
		end
	end
	return false
end

functions.getProducts = function()
	local productsArray: { product } = {}
	for _, productInfo: product in pairs(products) do
		table.insert(productsArray, productInfo)
	end
	return productsArray
end

functions.getTags = function()
	local tagsArray: { tag } = {}
	for _, tagInfo: tag in pairs(tags) do
		table.insert(tagsArray, tagInfo)
	end
	return tagsArray
end

events.purchaseProduct = function(player: Player, productId: number)
	if products[productId] then
		MarketplaceService:PromptProductPurchase(player, products[productId].productId)
	end
end

PlayerReady.OnServerEvent:Connect(function(player: Player)
	task.wait(0.5)

	if (serverIsOnline == nil and isServerOnline()) or serverIsOnline == true then
		PlayerReady:FireClient(player)
	end
end)

RemoteFunction.OnServerInvoke = function(player: Player, func: string, ...)
	if functions[func] ~= nil then
		return functions[func](player, ...)
	end
	return false
end

RemoteEvent.OnServerEvent:Connect(function(player: Player, func: string, ...)
	if events[func] ~= nil then
		events[func](player, ...)
	end
end)

task.spawn(function()
	while task.wait(90) do
		isServerOnline()
	end
end)
