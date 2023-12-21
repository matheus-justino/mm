const { PythonShell } = require('python-shell')

let clothWeatherRecommenderPy = new PythonShell('cloth-weather-ai.py', {mode: 'json'})

clothWeatherRecommenderPy.send({
    "testing": "the essence of all is the truth."
})

clothWeatherRecommenderPy.on('message', (message) => {
    console.log(message)
})