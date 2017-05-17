# ClickableRequires for Sublime Text 3

## Description
Open the required javascript files with a mouseclick as you are doing it in another IDEs.
The implementation of the file search is based on the Node.js's documentation.

> https://nodejs.org/api/modules.html#modules_all_together

## Installation
* clone the repository into Sublime Packages folder
* install through Package Control: `ClickableRequires`

## Usage
You can hover on any `require('module-name')` statement to open a pop-up with in-app link to the file.
For core node modules the online documentation will be opened in the browser.
If the file is from node_modules then also an npm link to the package will be displayed.

## Click settings
You can setup the plugin to navigate on mouseclick:
 * open the Pakages by Command Palette -> Browse Packages
 * in /Packages/User/ folder create or edit the `Default.sublime-mousemap` file
 * add the following (here you can modify the button and the modifiers as you like but beware with binding collosions.):

```json
[
  { "button": "button1", "modifiers": ["super"], "command": "open_require_under_cursor", "press_command": "drag_select" }
]
```

![demo](./demo.gif)

## Settings

The default settings are the following:

```javascript
{
  "debug": false,                 // To turn on or off file searching debug logs
  "reveal_in_side_bar": true,     // Will reveal the file in the sidebar
  "extensions": [".js", ".jsx"],  // The file extensions the plugin searches in
  "scope": "support.module",      // See more at https://www.sublimetext.com/docs/3/scope_naming.html
  "icon": "dot",                  // Possible values: dot, circle, bookmark and cross. Empty string for hidden icon.
  "underline": true,              // If the module names should be underlined
  "show_popup_on_hover": true     // If a popup with module link and path should appear on hovering the require statement
}
```

However you can override them in `Preferences -> Package Settings -> ClickableRequires -> Settings - User`.
