var NodeHelper = require("node_helper");
const { PythonShell } = require('python-shell')

module.exports = NodeHelper.create({
	getClothAI(){
		let clothPaletteRecommenderPy = new PythonShell('cloth-ai.py', {mode: 'json'})

		clothPaletteRecommenderPy.on('message', (message) => {
			this.sendSocketNotification("CLOTH-AI-RESPONSE", message)
		})
	},

	getClothWeather(){
		let clothWeatherRecommenderPy = new PythonShell('cloth-weather-ai.py', {mode: 'json'})

		clothWeatherRecommenderPy.on('message', (message) => {
			this.sendSocketNotification("CLOTH-WEATHER-AI-RESPONSE", message)
		})
	},

	socketNotificationReceived(notification, payload) {
		console.log(this.name + " recebeu uma notificação de um socket: " + notification + " - Payload: " + payload)

		if (notification === "CONFIG") {
			console.log('Iniciando ClothAI via node_helper...')
		} else if (notification === "GET-CLOTH"){
			this.getClothAI()
		} else if (notification === "CLOTH-WEATHER"){
			this.getClothWeather()
		}
	},

})