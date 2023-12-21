var NodeHelper = require("node_helper");
var fs = require('fs')
var http = require('http')
const { spawn } = require('child_process');
const path=require('path')

module.exports = NodeHelper.create({
	launchit(payload){
		let handler
		if(payload.debug) console.log("SpeechAI rodando "+payload.command+" usando "+payload.pythonName)

		handler = spawn(payload.pythonName, ['-u', payload.command]);

		handler.stdout.on('data', (data) => {
			if(payload.debug) console.log("SpeechAI enviando output="+data+" modulo="+payload.identifier)

			try{
				const dataStrRaw = data.toString()
				const dataStr = dataStrRaw.replaceAll("'", '"')
				const dataObj = JSON.parse(dataStr)

                console.log(dataObj)

				this.sendSocketNotification("message_from_helper", { identifier: payload.identifier, message: dataObj.action, data: dataObj } )
			} catch(e){
				console.log(data.toString())
			}
		})

		handler.stderr.on('data', (data)=>{
			if(payload.debug) console.log("SpeechAI erro no programa="+data)
		})

		handler.on('error', (error)=>{
			if(payload.debug) console.log("SpeechAI erro no instanciamento="+data)
		})
	},

	startit(payload){
		if(payload.command.startsWith(payload.pythonName))
			payload.command=payload.command.slice(payload.pythonName.length)
		if(payload.localfolder)
			payload.command=__dirname+path.sep+payload.command
		if(payload.repetitive)
			this.launchit(payload)
		else{
			this.launchit(payload)
		}

	},

	socketNotificationReceived(notification, payload) {
		console.log(this.name + " recebeu uma notificação de um socket: " + notification + " - Payload: " + payload);

		if (notification === "CONFIG") {
			this.startit(payload)
		}
	},
});