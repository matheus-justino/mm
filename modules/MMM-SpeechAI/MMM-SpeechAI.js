// Ouvir usuário...
// Categorias: cloth, climate_and_weather, news
// Exemplo:
// Quais são as notícias de hoje? -> news
// Vai chover hoje? -> climate_and_weather
// O que combina com essa calça? -> cloth
// -------- Fazer isso com o mDeBERTa e o wav2vec2

Module.register("MMM-SpeechAI", {
	defaults: {
		command: "",
		repetitive: true,
		cycletime:0,
		debug:false,
		transform: (data)=>{ return data.replace(/\n/g,"<br>")}
	},

	init: function(){
		Log.log(this.name + " rodando init.");
	},

	start: function(){			
		Log.log(this.name + " está iniciando.");
		if(this.config.command == ""){
			this.config.command=this.file("debug.py")
		}
	},

	notificationReceived: function(notification, payload, sender) {
		if(notification==="ALL_MODULES_STARTED"){
			let temp = this.config
			temp.identifier = this.identifier
			this.sendSocketNotification("CONFIG",temp)

			this.config.initializing = true
			this.config.initializationMessage = "Estou acordando..."

			const initMessages = ["Quase lá...", "Conectando..."]

			const changeInitMessage = setInterval(() => {
				if(this.config.initializing){
					this.config.initializationMessage = initMessages[Math.floor(Math.random()*initMessages.length)]
					this.updateDom(1000)
				} else{
					clearInterval(changeInitMessage)
				}
			}, 3000)
		}
	},

	socketNotificationReceived: async function(notification, payload) {
		Log.log(this.name + " recebeu a resposta do socket PYTHON (" + notification + ")\n\n - ACTION: " + payload.data.action);

        const dataObj = payload.data
		
		this.solListening = (state) => {
			if(state){
				this.config.solListening = true
				this.updateDom(1000)
			} else{
				this.config.solListening = false
				this.updateDom(1000)
			}
		}

		const sendAction = (action, message) => {
			this.sendNotification(action, {message: message})
			this.config.solListening = false
			this.updateDom(1000)
		}

		const actionCallbacks = {
			'turn-on-sol': () => {
				this.config.solListening = true
				this.updateDom(1000)
			},
			'cloth-module': () => {
				sendAction('CLOTH', 'get-clothes')
			},
			'weather-module': () => {
				sendAction('WEATHER', 'get-weather')
			},
			'news-module': () => {
				sendAction('NEWS', 'get-news')
			},
			'initializing-model': () => {
				this.config.initializing = true
				this.updateDom(1000)
			},
			'initialized-model': () => {
				this.config.initializing = false
				this.updateDom(1000)
			},
			'speechai-error': () => {
				this.config.error = true
				this.updateDom(1000)
				setTimeout(() => {
					this.config.error = false
					this.config.solListening = false
					this.updateDom(1000)
				}, 3000)
			},
			'command-not-recognized': () => {
				this.config.solListening = false
				this.config.notRecognized = true
				this.updateDom(1000)
				setTimeout(() => {
					this.config.notRecognized = false
					this.updateDom(1000)
				}, 3000)
			},
			'voice-activity': () => {
				this.config.voiceActivity = true
				this.updateDom(1000)
			},
			'voice-activity-off': () => {
				this.config.voiceActivity = false
				this.updateDom(1000)
			},
			'voice-activity-log': () => {
				this.config.voiceActivity = true
				console.log(`Voz detectada. => ${dataObj['audio-to-text']}`)
			}
		}

		try{
			actionCallbacks[dataObj.action]()
		} catch(e) {
			console.log(dataObj)
		}
	},

	suspend: function(){
	},

	resume: function(){
	},

	getTemplate: function() {
		return 'MMM-SpeechAI.njk';
	},

    getTemplateData: function () {
		return this.config;
	}
})
