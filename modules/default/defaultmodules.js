/* MagicMirror² Default Modules List
 * Modules listed below can be loaded without the 'default/' prefix. Omitting the default folder name.
 *
 * By Michael Teeuw https://michaelteeuw.nl
 * MIT Licensed.
 */

const defaultModulesConfig = ["alert", "calendar", "clock", "compliments", "helloworld", "newsfeed", "updatenotification", "weather"];

const defaultModules = ["alert", "clock", "compliments", "helloworld", "updatenotification"];

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") {
	module.exports = defaultModules;
}
