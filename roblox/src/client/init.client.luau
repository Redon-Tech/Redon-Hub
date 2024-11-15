--[[
	File: StarterPlayer/StarterPlayerScripts/Hub_Client
	Usage: The hub client.
	Do not edit unless you know what you are doing.
]]

local newTime = 604800 -- 1 week
-- I recomend if you change the above to use a time from https://unixtime.org/ at the section "What is the unix Timestamp?"

-- Init
if game:IsLoaded() == false then
	game.Loaded:Wait()
end

game:GetService("Players").LocalPlayer:WaitForChild("PlayerGui"):WaitForChild("StudioGui"):Destroy()

local ProgressBar = require(script.ProgressBar)

local LoadCircle = ProgressBar.new()
LoadCircle.AnchorPoint = Vector2.new(0.5, 0.5)
LoadCircle.Position = UDim2.fromScale(0.5, 0.5)
LoadCircle.BGColor = Color3.fromRGB(15, 37, 55)
LoadCircle:Animate("InfSpin1")
LoadCircle.Parent.DisplayOrder = 1

local StarterGui = game:GetService("StarterGui")
if not game:IsLoaded() then
	game.Loaded:Wait()
end
task.wait(1)
StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, false)
StarterGui:SetCore("ResetButtonCallback", false)

-- Types
type UIConfiguration = {
	BrandName: string,
	BrandImage: string,
	AboutUs: string,
	FeaturedProduct: string,
	UseCustomColors: boolean,
	Colors: { string: Color3 },
	cartEnabled: boolean,
}

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
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")
local TextService = game:GetService("TextService")
local Player = game:GetService("Players").LocalPlayer
local PlayerGui = Player.PlayerGui
local HubGui = PlayerGui:WaitForChild("HubGui")
local RemoteEvent = ReplicatedStorage:WaitForChild("RemoteEvent")
local RemoteFunction = ReplicatedStorage:WaitForChild("RemoteFunction")
local PlayerReady = ReplicatedStorage:WaitForChild("PlayerReady")

PlayerReady:FireServer()
PlayerReady.OnClientEvent:Wait()

local DefaultColors = {
	[Color3.fromRGB(15, 37, 55)] = "Background",
	[Color3.fromRGB(32, 55, 76)] = "BackgroundAccent",

	[Color3.fromRGB(65, 132, 197)] = "Primary",
	[Color3.fromRGB(66, 79, 92)] = "Secondary",
	[Color3.fromRGB(78, 156, 78)] = "Success",
	[Color3.fromRGB(77, 163, 189)] = "Info",
	[Color3.fromRGB(217, 164, 6)] = "Warning",
	[Color3.fromRGB(184, 71, 67)] = "Danger",
	[Color3.fromRGB(145, 155, 165)] = "Light",
	[Color3.fromRGB(32, 55, 76)] = "Dark",

	[Color3.fromRGB(255, 255, 255)] = "TextColor",
	[Color3.fromRGB(0, 0, 0)] = "AccentTextColor",

	[Color3.fromRGB(148, 166, 180)] = "ImageAccentColor",
}
local UIConfiguration: UIConfiguration = RemoteFunction:InvokeServer("getUIConfiguration")
local productsArray: { product } = RemoteFunction:InvokeServer("getProducts")
local products: { [number]: product } = {}
local productsByName: { [string]: product } = {}

for _, productInfo: product in pairs(productsArray) do
	products[productInfo.id] = productInfo
	productsByName[productInfo.name] = productInfo
end

local tags: { [number]: tag } = {}
local tagsArray = RemoteFunction:InvokeServer("getTags")
for _, tagInfo: tag in pairs(tagsArray) do
	tags[tagInfo.id] = tagInfo
end

local currentPage, currentPageIndex, lastPage = "Home", 1, "Home"

-- Functions

-- Init UI
local function lookupColor(color: Color3)
	for i, v in pairs(DefaultColors) do
		if color == i then
			return v
		end
	end

	return
end
if UIConfiguration.UseCustomColors == true then
	LoadCircle.BGColor = UIConfiguration.Colors["Background"]
	LoadCircle.Color = UIConfiguration.Colors["TextColor"]
	for i, v in pairs(HubGui:GetDescendants()) do
		if v:IsA("GuiObject") then
			local color = lookupColor(v.BackgroundColor3)
			if color and typeof(UIConfiguration.Colors[color]) == "Color3" then
				v.BackgroundColor3 = UIConfiguration.Colors[color]
			end
		end
		if v:IsA("TextLabel") or v:IsA("TextBox") or v:IsA("TextButton") then
			local textColor = lookupColor(v.TextColor3)
			if textColor and typeof(UIConfiguration.Colors[textColor]) == "Color3" then
				v.TextColor3 = UIConfiguration.Colors[textColor]
			end

			if v:IsA("TextBox") then
				local placeholderColor = v.PlaceholderColor3
				if placeholderColor and typeof(UIConfiguration.Colors[placeholderColor]) == "Color3" then
					v.PlaceholderColor3 = UIConfiguration.Colors[placeholderColor]
				end
			end
		end
		if v:IsA("ImageLabel") or v:IsA("ImageButton") and v.ImageColor3 ~= Color3.new(1, 1, 1) then
			local imageColor = v.ImageColor3
			if imageColor and typeof(UIConfiguration.Colors[imageColor]) == "Color3" then
				v.ImageColor3 = UIConfiguration.Colors[imageColor]
			end
		end
	end
end

for i, v: TextButton in pairs(HubGui:GetDescendants()) do
	if v:IsA("TextButton") then
		if v.Text == "Add To Cart" or v.Text == "Purchase" and v:GetAttribute("NoMod") ~= true then
			v.Text = if UIConfiguration.cartEnabled then "Add To Cart" else "Purchase"
		end
	end
end

if UIConfiguration.cartEnabled == false then
	HubGui.NavRight.Cart:Destroy()
	HubGui.Screens.Cart:Destroy()
end

if typeof(UIConfiguration.BrandName) == "string" then
	HubGui.NavTop.BrandName.Text = UIConfiguration.BrandName
else
	HubGui.NavTop.BrandName.Visible = false
end

if typeof(UIConfiguration.BrandImage) == "string" then
	HubGui.NavTop.BrandIcon.Image = UIConfiguration.BrandImage
else
	HubGui.NavTop.BrandIcon.Visible = false
end

if typeof(UIConfiguration.AboutUs) == "string" then
	HubGui.Screens.About.Container.About.Text = UIConfiguration.AboutUs
else
	HubGui.NavRight.About.Visible = false
end

if UIConfiguration.FeaturedProduct == nil or productsByName[UIConfiguration.FeaturedProduct] == nil then
	local featuredProduct = nil
	local featuredProductOwners = 0

	for _, productInfo: product in pairs(products) do
		if featuredProduct == nil or featuredProductOwners < productInfo.owners then
			featuredProduct = productInfo.name
			featuredProductOwners = productInfo.owners
		end
	end

	UIConfiguration.FeaturedProduct = featuredProduct
end

if UIConfiguration.FeaturedProduct and productsByName[UIConfiguration.FeaturedProduct] then
	local productInfo: product = productsByName[UIConfiguration.FeaturedProduct]

	HubGui.Screens.Home.FeaturedProduct.ProductName.Text = productInfo.name
	HubGui.Screens.Home.FeaturedProduct.ProductDescription.Text = productInfo.description
	HubGui.Screens.Home.FeaturedProduct.FeatureImage.Image = productInfo.imageId

	if productInfo["stock"] and productInfo.stock < 1 then
		HubGui.Screens.Home.FeaturedProduct.Button.BackgroundColor3 = if UIConfiguration.UseCustomColors
			then UIConfiguration.Colors["Light"]
			else Color3.fromRGB(145, 155, 165)
		HubGui.Screens.Home.FeaturedProduct.Button.Text = "Out of Stock"
	end
end

local ProductTemplate = HubGui.Screens.Home.PopularProducts.Products.ProductTemplate
ProductTemplate.Parent = script

-- Actual Functions
local function charAdded(char)
	char.HumanoidRootPart.Anchored = true
end
Player.CharacterAdded:Connect(charAdded)
if Player.Character then
	charAdded(Player.Character)
end
workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable

-- Page Switching
local switchPageDebounce = false
local function switchPage(page: string)
	if switchPageDebounce then
		return
	end
	if page == currentPage then
		return
	end
	if HubGui.Screens:FindFirstChild(page) == nil then
		return
	end
	if HubGui.Screens:FindFirstChild(currentPage) == nil then
		error("How?")
	end
	switchPageDebounce = true

	local startPosition, newCurrentDisplayPosition
	do
		if page == "Product" then
			startPosition = UDim2.fromScale(1.5, 0.5)
			newCurrentDisplayPosition = UDim2.fromScale(-1.5, 0.5)
		elseif currentPage == "Product" then
			startPosition = UDim2.fromScale(-1.5, 0.5)
			newCurrentDisplayPosition = UDim2.fromScale(1.5, 0.5)
		elseif currentPageIndex > HubGui.Screens[page].LayoutOrder then
			startPosition = UDim2.fromScale(0.5, -1.5)
			newCurrentDisplayPosition = UDim2.fromScale(0.5, 1.5)
		elseif currentPageIndex < HubGui.Screens[page].LayoutOrder then
			startPosition = UDim2.fromScale(0.5, 1.5)
			newCurrentDisplayPosition = UDim2.fromScale(0.5, -1.5)
		end
	end

	HubGui.Screens[page].Position = startPosition
	HubGui.Screens[page].Visible = true
	local t1 = TweenService:Create(
		HubGui.Screens[page],
		TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut),
		{ Position = UDim2.fromScale(0.5, 0.5) }
	)
	t1:Play()
	TweenService:Create(
		HubGui.Screens[currentPage],
		TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut),
		{ Position = newCurrentDisplayPosition }
	):Play()

	for _, button: Frame in pairs(HubGui.NavRight:GetChildren()) do
		if button:IsA("Frame") then
			--screen.Visible = if screen.Name == page then true else false
			TweenService:Create(
				button.BackgroundTransparency,
				TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut),
				{ Transparency = if button.Name == page then 0 else 1 }
			):Play()
		end
	end

	t1.Completed:Wait()
	HubGui.Screens[currentPage].Visible = false
	HubGui.Screens[currentPage].Position = UDim2.fromScale(0.5, 0.5)

	lastPage = currentPage
	currentPage = page
	currentPageIndex = HubGui.Screens[page].LayoutOrder
	switchPageDebounce = false
end
for _, screen: Frame in pairs(HubGui.Screens:GetChildren()) do
	if screen:IsA("Frame") then
		screen.Visible = false
	end
end
for _, button: Frame in pairs(HubGui.NavRight:GetChildren()) do
	if button:IsA("Frame") then
		button.BackgroundTransparency = if button.Name == "Home" then 0 else 1
	end
end
HubGui.Screens.Home.Visible = true

for _, button: Frame in pairs(HubGui.NavRight:GetChildren()) do
	if button:IsA("Frame") then
		local actualButton = button:FindFirstChildWhichIsA("ImageButton")
		if actualButton == nil then
			continue
		end
		actualButton.MouseButton1Click:Connect(function()
			switchPage(button.Name)
		end)
	end
end

HubGui.Screens.Product.Container.Title.Back.MouseButton1Click:Connect(function()
	switchPage("Products")
end)

UserInputService.InputBegan:Connect(function(input, gameProccessedEvent)
	if gameProccessedEvent then
		return
	end

	if input.KeyCode == Enum.KeyCode.Tab and not input:IsModifierKeyDown(Enum.ModifierKey.Shift) then
		local newPageIndex = currentPageIndex
		local newPage = nil
		local over = false
		repeat
			newPageIndex += 1
			if newPageIndex > #HubGui.Screens:GetChildren() then
				over = true
			end
			for _, screen: Frame in pairs(HubGui.ScreensLight:GetChildren()) do
				if screen:IsA("Frame") and screen.LayoutOrder == newPageIndex then
					newPage = screen
				end
			end
		until newPage ~= nil or over == true
		if currentPage == "Product" then
			newPage = HubGui.Screens[lastPage]
			over = false
		end
		if over then
			return
		end

		switchPage(newPage.Name)
	elseif input.KeyCode == Enum.KeyCode.Tab and input:IsModifierKeyDown(Enum.ModifierKey.Shift) then
		local newPageIndex = currentPageIndex
		local newPage = nil
		local over = false
		repeat
			newPageIndex -= 1
			if newPageIndex < 1 then
				over = true
			end
			for _, screen: Frame in pairs(HubGui.Screens:GetChildren()) do
				if screen:IsA("Frame") and screen.LayoutOrder == newPageIndex then
					newPage = screen
				end
			end
		until newPage ~= nil or over == true
		if currentPage == "Product" then
			newPage = HubGui.Screens[lastPage]
			over = false
		end
		if over then
			return
		end

		switchPage(newPage.Name)
	end
end)

-- Product Handling

local function purchaseProduct(product)
	if typeof(product) == "string" and productsByName[product] then
		product = productsByName[product]
	elseif typeof(product) == "number" and products[product] then
		product = products[product]
	end

	RemoteEvent:FireServer("purchaseProduct", product.id)
end
HubGui.Screens.Home.FeaturedProduct.Button.MouseButton1Click:Connect(function()
	purchaseProduct(HubGui.Screens.Home.FeaturedProduct.ProductName.Text)
end)
HubGui.Screens.Product.Container.ProductInfo.Controls.Purchase.MouseButton1Click:Connect(function()
	purchaseProduct(HubGui.Screens.Product.Container.ProductInfo.ProductName.Text)
end)

local function populateTagsFrame(productFrame: Frame, productInfo: product)
	local tagsFrame = productFrame:FindFirstChild("Tags")
	if tagsFrame == nil then
		return
	end

	for i, v in pairs(tagsFrame:GetChildren()) do
		if v:IsA("TextLabel") then
			v:Destroy()
		end
	end

	local spaceAvaliable = tagsFrame.AbsoluteSize.X

	if productInfo.createdAt.UnixTimestamp > DateTime.now().UnixTimestamp - newTime then
		local tag = Instance.new("TextLabel")
		tag.Name = "Tag"
		tag.FontFace =
			Font.new("rbxasset://fonts/families/SourceSansPro.json", Enum.FontWeight.Bold, Enum.FontStyle.Normal)
		tag.Text = "NEW"
		tag.TextColor3 = if UIConfiguration.UseCustomColors
			then UIConfiguration.Colors["TextColor"]
			else Color3.fromRGB(255, 255, 255)
		tag.TextScaled = true
		tag.AnchorPoint = Vector2.new(0.5, 0.5)
		tag.BackgroundColor3 = if UIConfiguration.UseCustomColors
			then UIConfiguration.Colors["Primary"]
			else Color3.fromRGB(78, 156, 78)
		tag.Position = UDim2.fromScale(0.5, 0.5)
		tag.Size = UDim2.fromScale(0.395, 0.625)

		local uICorner = Instance.new("UICorner")
		uICorner.Name = "UICorner"
		uICorner.CornerRadius = UDim.new(0.3, 0)
		uICorner.Parent = tag

		tag.Parent = tagsFrame
		spaceAvaliable -= tag.AbsoluteSize.X
	end

	local fontSize = 0.625 * tagsFrame.AbsoluteSize.Y
	for _, tagId in ipairs(productInfo.tags) do
		if tags[tagId] then
			local tagInfo: tag = tags[tagId]
			local textSize: Vector2 = TextService:GetTextSize(
				tagInfo.name,
				fontSize,
				Enum.Font.SourceSansBold,
				Vector2.new(tagsFrame.AbsoluteSize.X, fontSize)
			)
			--print(tagInfo.name, textSize.X + 35, spaceAvaliable)

			if textSize.X + 35 > spaceAvaliable then
				continue
			end

			local tag = Instance.new("TextLabel")
			tag.Name = "Tag"
			tag.FontFace =
				Font.new("rbxasset://fonts/families/SourceSansPro.json", Enum.FontWeight.Bold, Enum.FontStyle.Normal)
			tag.Text = tagInfo.name
			tag.TextColor3 = tagInfo.textColor
			tag.TextScaled = true
			tag.AnchorPoint = Vector2.new(0.5, 0.5)
			tag.BackgroundColor3 = tagInfo.color
			tag.Position = UDim2.fromScale(0.5, 0.5)
			tag.Size = UDim2.new(0, textSize.X + 35, 0.625, 0)

			local uICorner = Instance.new("UICorner")
			uICorner.Name = "UICorner"
			uICorner.CornerRadius = UDim.new(0.3, 0)
			uICorner.Parent = tag

			tag.Parent = tagsFrame
			spaceAvaliable -= tag.AbsoluteSize.X
		end
	end
end

local function formatRobux(robux: number): string
	local rounded = math.floor(robux * 100 + 0.5) / 100
	local _, _, minus, int, fraction = tostring(rounded):find("([-]?)(%d+)([.]?%d*)")
	int = int:reverse():gsub("(%d%d%d)", "%1,")
	local formattedRobux = minus .. int:reverse():gsub("^,", "") .. fraction
	return `R${formattedRobux}`
end

local function openProductPage(product: product)
	local productInfo = HubGui.Screens.Product.Container.ProductInfo
	productInfo.ProductName.Text = product.name
	productInfo.ProductDescription.Text = product.description
	productInfo.ProductPrice.Text = formatRobux(product.price)
	if typeof(product.stock) == "number" then
		productInfo.ProductStock.Text = `{product.stock} Stock Left`
	else
		productInfo.ProductStock.Text = "Unlimited Stock Left"
	end
	productInfo.FeatureImage.Image = product.imageId

	switchPage("Product")
end
HubGui.Screens.Home.FeaturedProduct.FeatureImage.MouseButton1Click:Connect(function()
	openProductPage(productsByName[HubGui.Screens.Home.FeaturedProduct.ProductName.Text])
end)

-- Populate Product Lists

-- Popular Products
table.sort(productsArray, function(a, b)
	return a.purchases > b.purchases
end)
for position, productInfo: product in pairs(productsArray) do
	local productFrame = ProductTemplate:Clone()
	productFrame.LayoutOrder = position
	productFrame.Name = productInfo.name
	productFrame.ProductImage.Image = productInfo.imageId
	productFrame.ProductName.Text = productInfo.name
	productFrame.ProductPrice.Text = formatRobux(productInfo.price)

	local function productClick()
		openProductPage(productInfo)
	end
	productFrame.Button.MouseButton1Click:Connect(productClick)

	productFrame.Parent = HubGui.Screens.Home.PopularProducts.Products
	populateTagsFrame(productFrame, productInfo)
end

-- Products Page
local nameSort = {}
for _, productInfo: product in pairs(productsArray) do
	table.insert(nameSort, productInfo.name)
end
table.sort(nameSort)
for position, productName in ipairs(nameSort) do
	local productInfo: product = productsByName[productName]
	local productFrame = ProductTemplate:Clone()
	productFrame.LayoutOrder = position
	productFrame.Name = productInfo.name
	productFrame.ProductImage.Image = productInfo.imageId
	productFrame.ProductName.Text = productInfo.name
	productFrame.ProductPrice.Text = formatRobux(productInfo.price)

	local function productClick()
		openProductPage(productInfo)
	end
	productFrame.Button.MouseButton1Click:Connect(productClick)

	productFrame.Parent = HubGui.Screens.Products.Container.Products
	populateTagsFrame(productFrame, productInfo)

	HubGui.Screens.Products.Container.Products:GetAttributeChangedSignal("Search"):Connect(function()
		if string.find(productInfo.name:lower(), HubGui.Screens.Products.Container.Products:GetAttribute("Search")) then
			productFrame.Visible = true
		else
			productFrame.Visible = false
		end
	end)
end

-- Search box
HubGui.NavTop.Search.SearchBox:GetPropertyChangedSignal("Text"):Connect(function()
	if HubGui.NavTop.Search.SearchBox.Text == "" or HubGui.NavTop.Search.SearchBox.Text == nil then
		HubGui.Screens.Products.Container.Products:SetAttribute("Search", "")
	else
		switchPage("Products")
		HubGui.Screens.Products.Container.Products:SetAttribute("Search", HubGui.NavTop.Search.SearchBox.Text:lower())
	end
end)

local function isVerified()
	local data = RemoteFunction:InvokeServer("isVerified")

	if data == true then
		return true
	elseif typeof(data) == "string" then
		return data
	end

	return
end

local function verificationScreen()
	local currentVerificationStatus = isVerified()

	if currentVerificationStatus == true then
		HubGui.Verify.Visible = false
		HubGui.NavTop.Visible = true
		HubGui.NavRight.Visible = true
		HubGui.Screens.Visible = true
	else
		HubGui.Verify.Code.Text = `/verify link <b>{currentVerificationStatus}</b>`
		HubGui.Verify.Visible = true
		HubGui.Verify.Continue.MouseButton1Click:Connect(function()
			if isVerified() == true then
				HubGui.Verify.Visible = false
				HubGui.NavTop.Visible = true
				HubGui.NavRight.Visible = true
				HubGui.Screens.Visible = true
			else
				HubGui.Verify.Failed.Visible = true
				task.delay(5, function()
					HubGui.Verify.Failed.Visible = false
				end)
			end
		end)
	end
end

-- Finish
print("Loaded!")
LoadCircle.Parent:Destroy()
verificationScreen()
