# ClickableRequires for Sublime Text 3

## Description
Open the required javascript files with a mouseclick as you are doing it in another IDEs.
The implementation of the file search is based on the specification of require function in Node.js.

> https://nodejs.org/api/modules.html#modules_all_together

> :sunglasses:  Now ES6 import statements are supported as well. :sunglasses:

## Installation
* clone the repository into Sublime Packages folder
* install through Package Control: `ClickableRequires`

## Usage
You can hover on any `require('module-name')` or `import module from 'module'` statements to open a pop-up with in-app link to the file.
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
  "extensions": [ ".js", ".jsx", ".ts", ".tsx", ".vue" ], // Allowed file extensions to search for import and require statements
  "resolve_extensions": [ ".js", ".jsx", ".ts", ".tsx", ".vue", ".node", ".json" ], // The module finder will try to resolve to these extensions when searching without concrete extension
  "scope": "support.module",      // See more at https://www.sublimetext.com/docs/3/scope_naming.html
  "icon": "dot",                  // Possible values: dot, circle, bookmark and cross. Empty string for hidden icon.
  "underline": true,              // If the module names should be underlined
  "show_popup_on_hover": true,    // If a popup with module link and path should appear on hovering the require statement
  "auto_fold_imports": false      // Fold lines with import when opening file
}
```

However you can override them in `Preferences -> Package Settings -> ClickableRequires -> Settings - User`.

## Webpack or other module handlers

If you are using webpack `resolve.modules` or `resolve.aliases` then you should configure the routes to this modules in your `.sublime-project` file.
Use relative paths to the project file!

```json
{
  "folders":
  [
    {
      "path": "."
    }
  ],
  "settings":
  {
     "webpack_resolve_modules": ["src", "other_module_directory"],
     "webpack_resolve_extensions": [".js", ".jsx", ".json"]
  }
}
```