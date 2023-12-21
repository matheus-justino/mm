Module.register("MMM-WeatherAI", {
	getWeather: function () {
		if(navigator.geolocation){
			navigator.geolocation.getCurrentPosition((pos) => {
				const latitude = pos.coords.latitude
				const longitude = pos.coords.longitude
	
				let dataObj = {
					'message': '',
					'forecastCondition': {},
					'currentTemp': '',
					'currentCondition': {},
					'location': {
						'name': '',
						'region': ''
					}
				}
			
				const forecastTimes = {
					0: 'Ao amanhecer',
					1: 'Ao amanhecer',
					2: 'Ao amanhecer',
					3: 'Ao amanhecer',
					4: 'Durante a manhã',
					5: 'Durante a manhã',
					6: 'Durante a manhã',
					7: 'Durante a manhã',
					8: 'Ao meio dia',
					9: 'Ao meio dia',
					10: 'Ao meio dia',
					11: 'À tarde',
					12: 'À tarde',
					13: 'Durante a tarde',
					14: 'Durante a tarde',
					15: 'Durante a tarde',
					16: 'Ao anoitecer',
					17: 'Durante a noite',
					18: 'Durante a noite',
					19: 'Durante a noite',
					20: 'Durante a noite',
					21: 'Amanhã',
					22: 'Amanhã',
					23: 'Amanhã'
				}
			
	
				fetch(`http://api.weatherapi.com/v1/forecast.json?key=5c74affbd4a748bda72162536231312&q=${latitude},${longitude}&days=3&aqi=no&alerts=no`)
					.then((res) => {
						const now = new Date()
						res.json().then((data) => {
							console.log(data)
							
							dataObj.location.name = data.location.name
							dataObj.location.region = data.location.region
		
							const forecastHours = data.forecast.forecastday[0].hour
		
							for(let hour in forecastHours){
								if(forecastHours[hour].time.slice(8,10) == now.getDate() && now.getHours() <= 20 && parseInt(forecastHours[hour].time.slice(11,13)) == now.getHours()+3){
									const currentTemp = data.current.temp_c
									const futureTemp = forecastHours[hour].temp_c
		
									console.log(forecastHours[hour])

									const willItRainHour = forecastHours[hour].will_it_rain
									const willItRain = data.forecast.forecastday[0].day.daily_will_it_rain
		
									if(futureTemp > currentTemp){
										if(willItRain == 1 && willItRainHour == 0){
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai subir. Haverá chuva.`
										}
										else if(willItRain == 1 && willItRainHour == 1){
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai subir e vai estar chovendo.`
										} else{
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai subir.`
										}
									} else if(futureTemp < currentTemp){
										if(willItRain == 1 && willItRainHour == 0){
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai diminuir. Haverá chuva.`
										}
										else if(willItRain == 1 && willItRainHour == 1){
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai diminuir e vai estar chovendo.`
										} else{
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai diminuir.`
										}
									} else{
										if(willItRain == 1 && willItRainHour == 0){
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai se manter. Haverá chuva.`
										}
										else if(willItRain == 1 && willItRainHour == 1){
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai se manter e vai estar chovendo.`
										} else{
											dataObj.message = `${forecastTimes[now.getHours()]}, a temperatura vai se manter.`
										}
									}
								}
		
								if(now.getHours() > 20){
									const tomorrow = data.forecast.forecastday[1].day
									const today = data.forecast.forecastday[0].day
		
									dataObj.message = `${tomorrow.maxtemp_c < today.maxtemp_c ? 'Amanhã, a temperatura vai subir um pouco' : 'Amanhã, a temperatura vai diminuir um pouco'} e ${tomorrow.daily_will_it_rain > 0 ? 'haverá chuva.' : 'não haverá chuva.'}`
		
									dataObj.forecastCondition = tomorrow.condition
								}
							}
		
							dataObj.currentCondition = data.current.condition
							dataObj.currentTemp = data.current.temp_c
		
							this.config.weatherData = dataObj
							this.config.loadedWeather = true
		
							console.log(dataObj)
							this.updateDom(1000)
						})
					})
			},(err ) =>{
				alert("getting error : " + err.message);
			  } , {timeout:10000})
		} else {
			alert('not supported.')
		}
	},

	getWeatherPy: function () {
		if(navigator.geolocation){
			navigator.geolocation.getCurrentPosition((pos) => {
				const latitude = pos.coords.latitude
				const longitude = pos.coords.longitude
	
				let dataObj = {
					"message": "",
					"forecastCondition": {},
					"currentTemp": "",
					"currentCondition": {},
					"location": {
						"name": "",
						"region": ""
					}
				}
			
				const forecastTimes = {
					0: "Ao amanhecer",
					1: "Ao amanhecer",
					2: "Ao amanhecer",
					3: "Ao amanhecer",
					4: "Durante a manhã",
					5: "Durante a manhã",
					6: "Durante a manhã",
					7: "Durante a manhã",
					8: "Ao meio dia",
					9: "Ao meio dia",
					10: "Ao meio dia",
					11: "À tarde",
					12: "À tarde",
					13: "Durante a tarde",
					14: "Durante a tarde",
					15: "Durante a tarde",
					16: "Ao anoitecer",
					17: "Durante a noite",
					18: "Durante a noite",
					19: "Durante a noite",
					20: "Durante a noite",
					21: "Amanhã",
					22: "Amanhã",
					23: "Amanhã"
				}
			
	
				fetch(`http://api.weatherapi.com/v1/forecast.json?key=5c74affbd4a748bda72162536231312&q=${latitude},${longitude}&days=3&aqi=no&alerts=no`)
					.then((res) => {
						const now = new Date()
						res.json().then((data) => {
							console.log(data)
							
							dataObj.location.name = data.location.name
							dataObj.location.region = data.location.region
		
							const forecastHours = data.forecast.forecastday[0].hour
		
							for(let hour in forecastHours){
								if(forecastHours[hour].time.slice(8,10) == now.getDate() && now.getHours() <= 20 && parseInt(forecastHours[hour].time.slice(11,13)) == now.getHours()+3){
									const currentTemp = data.current.temp_c
									const futureTemp = forecastHours[hour].temp_c
		
									console.log(forecastHours[hour])

									const willItRainHour = forecastHours[hour].will_it_rain
									const willItRain = data.forecast.forecastday[0].day.daily_will_it_rain

									dataObj.willItRain = willItRain
								}
		
								if(now.getHours() > 20){
									const tomorrow = data.forecast.forecastday[1].day
									const today = data.forecast.forecastday[0].day
		
									dataObj.message = `${tomorrow.maxtemp_c < today.maxtemp_c ? "Amanhã, a temperatura vai subir um pouco" : "Amanhã, a temperatura vai diminuir um pouco"} e ${tomorrow.daily_will_it_rain > 0 ? "haverá chuva." : "não haverá chuva."}`
		
									dataObj.forecastCondition = tomorrow.condition
								}
							}
		
							dataObj.current = data.current
							dataObj.currentTemp = data.current.temp_c
		
							this.sendNotification("CLOTH-WEATHER-TO-PY", dataObj)
						})
					})
			},(err ) =>{
				alert("getting error : " + err.message);
			  } , {timeout:10000})
		} else {
			alert("not supported.")
		}
	},

	notificationReceived: function(notification, payload, sender) {
		if(notification==="ALL_MODULES_STARTED"){
			this.getWeather()
		} else if(notification === "WEATHER"){
			this.getWeather()
			this.sendNotification("CLOTH-WEATHER")
		}
	},

	socketNotificationReceived: async function(notification, payload) {
	},

	suspend: function(){
	},

	resume: function(){
	},

	getTemplate: function() {
		return 'MMM-WeatherAI.njk';
	},

    getTemplateData: function () {
		return this.config;
	}
})
