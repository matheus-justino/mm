var NodeHelper = require("node_helper");
var fs = require('fs')
var http = require('http')
const { spawn } = require('child_process');
const path=require('path')

module.exports = NodeHelper.create({
	socketNotificationReceived(notification, payload) {
	},
});