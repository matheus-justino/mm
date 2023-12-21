Module.register("MMM-FaceAI", {
	defaults: {
		command: "",
		repetitive: true,
		cycletime:0,
		localfolder:false,
		pythonName:"python",
		debug:false,
		transform: (data)=>{ return data.replace(/\n/g,"<br>")}
	},

	init: function(){
		Log.log(this.name + " rodando init.");
	},

	start: function(){
		Log.log(this.name + " está iniciando.");
		if(this.config.command == "")
			this.config.command=this.file("debug.py")
	},

	notificationReceived: function(notification, payload, sender) {
		if(notification==="ALL_MODULES_STARTED"){
			let temp = this.config
			temp.identifier = this.identifier
			this.sendSocketNotification("CONFIG",temp)
		}

	},

	socketNotificationReceived: function(notification, payload) {
		Log.log(this.name + " recebeu a resposta do socket PYTHON (" + notification + ")\n\n - Payload: " + payload.message);
		if(notification === "message_from_helper" && payload.identifier == this.identifier){
			this.config.message = payload.message;
			this.updateDom(1000)
		}

	},

	suspend: function(){
	},

	resume: function(){
	},

	getTemplate: function() {
        wrapper = 'MMM-FaceAI.njk'

		return wrapper;
	},

    getTemplateData: function () {
		return this.config;
	}
})
