Module.register("MMM-ClothAI", {
	defaults: {
		message:'none',
		data:'none'
	},

	notificationReceived: function(notification, payload, sender) {
		if(notification==="ALL_MODULES_STARTED"){
			this.sendSocketNotification("CONFIG", {})
		} else if(notification === "CLOTH"){
			console.log('Enviando solicitação de inicialização do módulo.')
			this.sendSocketNotification("GET-CLOTH", {})
		} else if(notification === "CLOTH-WEATHER"){
			this.sendSocketNotification("CLOTH_WEATHER", payload)
		}
	},

	socketNotificationReceived: async function(notification, clothResponse) {
		if(notification === "CLOTH-AI-RESPONSE"){
			let stateConfig = {
			}
			
			stateConfig.imageLoading = true
			stateConfig.loadedCloth = false
			stateConfig.clothData = clothResponse
			stateConfig.imageMatches = []

			const loadingMessages = ['Hmm...', 'Que tal...', 'Vejamos...']
			stateConfig.loadingMessages = loadingMessages
			
			const labelsToLabels = {
				'Upper-clothes': 'Roupas do torso',
				'Dress': 'Vestido',
				'Pants': 'Calças',
				'Skirt': 'Saia',
				'Left-shoe': 'Calçado esquerdo',
				'Right-shoe': 'Calçado direito'
			}
			stateConfig.labelsToLabels = labelsToLabels

			const libraryFilesArrayJson = await fetch('/MMM-ClothAI/predictionsLibrary/libraryData.json')
			const libraryFilesArrayData = await libraryFilesArrayJson.json()
			console.log("Endereços da biblioteca de roupas: \n")
			console.log(libraryFilesArrayData)
			const libraryFilesArray = libraryFilesArrayData.clothes

			var libraryColors = []

			for(let file in libraryFilesArray){
				const clothDataJson = await fetch(`/MMM-ClothAI/predictionsLibrary/${libraryFilesArray[file]}`)
				const clothData = await clothDataJson.json()

				for(var label in clothData){
					libraryColors.push({
						name: libraryFilesArray[file],
						label: label,
						rgb: {
							r: clothData[label].dominant_color[0],
							g: clothData[label].dominant_color[1],
							b: clothData[label].dominant_color[2]
						}
					})
				}
			}

			const closestClothColor = (targetColor, colorArray) => {
				let closestDistance = 10000;
				let closestColor = null;
				
				const r1 = targetColor.r
				const g1 = targetColor.g
				const b1 = targetColor.b

				colorArray.forEach((color) => {
					const r2 = color.rgb.r
					const g2 = color.rgb.g
					const b2 = color.rgb.b
				  
					const distance = Math.sqrt(
						(r1 - r2) ** 2 +
						(g1 - g2) ** 2 +
						(b1 - b2) ** 2
					);
				  
					if (distance < closestDistance) {
						closestDistance = distance;
						closestColor = color;
					}
				});
				
				return closestColor;
			}

			stateConfig.showTakenPicture = false

			for(var clothLabel in clothData){
				const target = {
					r: clothData[clothLabel].dominant_color[0],
					g: clothData[clothLabel].dominant_color[1],
					b: clothData[clothLabel].dominant_color[2]
				}

				const closestColor = closestClothColor(target, libraryColors)

				const clothDataJson = await fetch(`MMM-ClothAI/predictionsLibrary/${closestColor.name}`)
				const clothData = await clothDataJson.json()

				const recommendationObj = {
					'Upper-clothes': 'Pants',
					'Pants': 'Upper-clothes',
					'Dress': 'Dress'
				}
				
				const responseObj = {
					'Upper-clothes': ['Encontrei uma camisa que cairia bem com essa calça!', 'Acho que sua calça ficaria muito boa com essa camisa!'] ,
					'Pants': ['Acho que sua camisa combinaria bem com essa calça!', 'Encontrei uma calça que combinaria bem com sua camisa!', 'Sua camisa cairia bem com essa calça!']
				}

				var labelCount = []
				var labelCountMatch = []

				for(var countLabel in clothData){
					labelCount.push(countLabel)
				}

				for(var countLabel in clothData){
					labelCountMatch.push(countLabel)
				}

				console.log(labelCount)

				i = 1
				for(var label in clothData){
					if(recommendationObj[clothLabel] == label){
						imageMatches.push({
							top_text: responseObj[label][Math.floor(Math.random()*responseObj[label].length)],
							image_url: `MMM-ClothAI/predictionsLibrary/${closestColor.name.slice(0, closestColor.name.length-5)}-${label}.png`,
							color: `${clothData[label].dominant_color.join(',')}`
						})
					}
					i++
				}
				
				stateConfig.loadedCloth = true

				this.config = stateConfig
				this.updateDom(1000)

				setTimeout(() => {
					this.config.loadedCloth = false
					this.updateDom(1000)
				}, 10000)
			}
		} else if(notification === "CLOTH-WEATHER-AI-RESPONSE"){
			alert('received that')
			console.log(clothResponse)
		}
	},

	suspend: function(){
	},

	resume: function(){
	},

	getTemplate: function() {
		return 'MMM-ClothAI.njk';
	},

    getTemplateData: function () {
		return this.config;
	}
})
