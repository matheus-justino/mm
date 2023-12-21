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
		}
	},

	socketNotificationReceived: async function(notification, payload) {
		Log.log(this.name + " recebeu a resposta do socket PYTHON (" + notification + ")\n\n - ACTION: " + payload.data.action);

        const dataObj = payload.data

		const actionCallbacks = {
			'turn-on-estela': () => {
				this.config.estelaListening = true
				// Ouvir usuário...
				// Categorias: cloth, climate_and_weather, news
				// Exemplo:
				// Quais são as notícias de hoje? -> news
				// Vai chover hoje? -> climate_and_weather
				// O que combina com essa calça? -> cloth
				// -------- Fazer isso com o mDeBERTa e o wav2vec2

				this.updateDom(1000)
			},
			'cloth-module': () => {
				this.sendNotification("CLOTH", {message: 'get-clothes'})
				this.config.estelaListening = false
				this.updateDom(1000)
			},
			'weather-module': () => {
				this.sendNotification("WEATHER", {message: 'get-clothes'})
				this.config.estelaListening = false
				this.updateDom(1000)
			},
			'news-module': () => {
				this.sendNotification("NEWS", {message: 'get-clothes'})
				this.config.estelaListening = false
				this.updateDom(1000)
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
					this.config.estelaListening = false
					this.updateDom(1000)
				}, 3000)
			},
			'command-not-recognized': () => {
				this.config.estelaListening = false
				this.config.notRecognized = true
				this.updateDom(1000)
				setTimeout(() => {
					this.config.notRecognized = false
					this.updateDom(1000)
				}, 3000)
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
        wrapper = 'MMM-SpeechAI.njk'

		return wrapper;
	},

    getTemplateData: function () {
		return this.config;
	}
})
