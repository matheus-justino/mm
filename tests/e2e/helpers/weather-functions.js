const { injectMockData } = require("../../utils/weather_mocker");
const helpers = require("./global-setup");

exports.getText = async (element, result) => {
	const elem = await helpers.waitForElement(element);
	expect(elem).not.toBe(null);
	expect(
		elem.textContent
			.trim()
			.replace(/(\r\n|\n|\r)/gm, "")
			.replace(/[ ]+/g, " ")
	).toBe(result);
};

exports.startApp = async (configFileName, additionalMockData) => {
	await helpers.startApplication(injectMockData(configFileName, additionalMockData));
	await helpers.getDocument();
};
