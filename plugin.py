import sublime
import sublime_plugin
import os
import re
import json
import webbrowser

REGEXP = '(require\s*\(\s*[\'"])(.+?)([\'"]\s*\))'

# |--------------------------------------------------------------------------
# | Main Command
# |--------------------------------------------------------------------------

class OpenRequireUnderCursorCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    view = self.view
    require_statements = view.find_all(REGEXP)
    cursor_position = view.sel()[0]

    for require_statement in require_statements:
      if cursor_position.intersects(require_statement):
        statement = view.substr(require_statement)
        module = re.match(REGEXP, statement).group(2)
        return open_node_module(view.window(), module)

class RequireEventListener(sublime_plugin.EventListener):

  def on_load_async(self, view):
    self._underline_regions(view)

  def on_modified_async(self, view):
    self._underline_regions(view)

  def on_hover(self, view, point, hover_zone):
    if not get_setting('show_popup_on_hover') \
      or not self._assert_in_right_file(view):
      return

    regions = self._find_regions(view)

    for region in regions:
      if region.contains(point):
        statement = view.substr(region)
        module = re.match(REGEXP, statement).group(2)
        return self._show_popup(view, module, point)

  def on_pre_close(self, view):
    if (hasattr(self, 'view_regions')) and (view.id() in self.view_regions):
      del self.view_regions[view.id()]

  def _find_regions(self, view):
    if not hasattr(self, 'view_regions'):
      self.view_regions = {}

    if 'require_regions' in self.view_regions:
      return self.view_regions['require_regions']

    regions = view.find_all(REGEXP)

    self.view_regions[view.id()] = regions

    return regions

  def _underline_regions(self, view):
    if not self._assert_in_right_file(view): return

    regions = self._find_regions(view)

    for region in regions:
      statement = view.substr(region)
      match = re.match(REGEXP, statement)

      region.a += len(match.group(1))
      region.b -= len(match.group(3))

    scope = get_setting('scope')
    icon = get_setting('icon')
    underline = get_setting('underline')

    underline_bitmask = sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE

    if underline:
      underline_bitmask |= sublime.DRAW_STIPPLED_UNDERLINE

    view.add_regions('requires',  regions, scope, icon, underline_bitmask)

  def _show_popup(self, view, module, point):
    window = view.window()
    ctx = window.extract_variables()
    file_path = ctx['file_path']

    file = find_module(module, file_path)

    link = 'Module: <a href="%s">%s</a>' % (module, module)

    if not returnIfFile(file):
      link += ' (opens browser)'
      description = '<p>Node.js core module</p>'
    else:
      description = '<p>Found at: %s</p>' % file
      if not module.startswith('.'):
        description += '<br/><a href="npm_%s">View on npmjs.com</a>' % module.split('/')[0]

    html = link + description
    width = (len(description) - 5) * 10
    view.show_popup(html, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, width, on_navigate = lambda module: self._on_anchor_clicked(window, module))

  def _on_anchor_clicked(self, window, module):
    if module.startswith('npm_'):
      return webbrowser.open('https://www.npmjs.com/package/' + module[len('npm_'):], autoraise=True)
    open_node_module(window, module)

  def _assert_in_right_file(self, view):
    window = view.window()
    if not window: return False

    ctx = window.extract_variables()
    if not 'file_name' in ctx: return False
    file_name = ctx['file_name']

    exts = get_setting('extensions')

    if not file_name.endswith(tuple(exts)):
      return False

    return True


# |--------------------------------------------------------------------------
# | Utility functions
# |--------------------------------------------------------------------------

SETTINGS_FILE = 'ClickableRequires.sublime-settings'

def get_setting(name):
  return sublime.load_settings(SETTINGS_FILE).get(name)

def log(*str):
  if get_setting('debug'): print(*str)

def returnIfFile(path, file = None):
  _file = path

  if file:
    _file = os.path.join(path, file)

  if os.path.isfile(_file):
    return _file

# |--------------------------------------------------------------------------
# | The pseudocode of require: https://nodejs.org/api/modules.html#modules_all_together
# |--------------------------------------------------------------------------

def open_node_module(window, module):
  ctx = window.extract_variables()
  file_path = ctx['file_path']

  match = find_module(module, file_path)

  if match:
    file = returnIfFile(match)

    if file:
      window.open_file(file)
      if get_setting('reveal_in_side_bar'):
        sublime.set_timeout(lambda: window.run_command('reveal_in_side_bar'), 100)
    else:
      webbrowser.open('https://nodejs.org/api/%s.html' % match, autoraise=True)

"""
require(X) from module at path Y
  1. If X is a core module,
     a. return the core module
     b. STOP
  2. If X begins with '/'
     a. set Y to be the filesystem root
  3. If X begins with './' or '/' or '../'
     a. LOAD_AS_FILE(Y + X)
     b. LOAD_AS_DIRECTORY(Y + X)
  4. LOAD_NODE_MODULES(X, dirname(Y))
  5. THROW "not found"
"""
def find_module(module, file_path):
  if module in CORE_MODULES:
    return module

  if module.startswith('.'):
    path = os.path.normpath(os.path.join(file_path, module))
    return load_as_file(path) or load_as_directory(path)

  return load_node_modules(module, file_path)

"""
LOAD_AS_FILE(X)
  1. If X is a file, load X as JavaScript text.  STOP
  2. If X.js is a file, load X.js as JavaScript text.  STOP
  3. If X.json is a file, parse X.json to a JavaScript Object.  STOP
  4. If X.node is a file, load X.node as binary addon.  STOP
"""
def load_as_file(path):
  log('load_as_file: ', path)
  return returnIfFile(path) \
    or returnIfFile(path + '.js') \
    or returnIfFile(path + '.json') \
    or returnIfFile(path + '.node')

"""
LOAD_AS_DIRECTORY(X)
  1. If X/package.json is a file,
     a. Parse X/package.json, and look for "main" field.
     b. let M = X + (json main field)
     c. LOAD_AS_FILE(M)
     d. LOAD_INDEX(M)
  2. LOAD_INDEX(X)
"""
def load_as_directory(path):
  log('load_as_directory: ', path)
  package_path = returnIfFile(path, 'package.json')
  if package_path:
    with open(package_path, 'r', encoding='UTF-8') as package_json_contents:
      package_json = json.load(package_json_contents)
      main = package_json.get('main', 'index.js')
      main_path = os.path.join(path, main)
      return load_as_file(main_path) or load_index(main_path)
  else:
    return load_index(path)

"""
LOAD_INDEX(X)
  1. If X/index.js is a file, load X/index.js as JavaScript text.  STOP
  2. If X/index.json is a file, parse X/index.json to a JavaScript object. STOP
  3. If X/index.node is a file, load X/index.node as binary addon.  STOP
"""
def load_index(path):
  log('load_index: ', path)
  return returnIfFile(path, 'index.js') \
    or returnIfFile(path, 'index.json') \
    or returnIfFile(path, 'index.node')

"""
LOAD_NODE_MODULES(X, START)
  1. let DIRS=NODE_MODULES_PATHS(START)
  2. for each DIR in DIRS:
     a. LOAD_AS_FILE(DIR/X)
     b. LOAD_AS_DIRECTORY(DIR/X)
"""
def load_node_modules(module, start):
  log('load_node_modules: ', module, ' - ', start)
  dirs = node_modules_paths(start)
  for dir in dirs:
    path = os.path.join(dir, module)
    file = load_as_file(path) or load_as_directory(path)
    # Return only if the file is found!
    if file: return file

"""
NODE_MODULES_PATHS(START)
  1. let PARTS = path split(START)
  2. let I = count of PARTS - 1
  3. let DIRS = []
  4. while I >= 0,
     a. if PARTS[I] = "node_modules" CONTINUE (## this makes no sense :/)
     b. DIR = path join(PARTS[0 .. I] + "node_modules")
     c. DIRS = DIRS + DIR
     d. let I = I - 1
  5. return DIRS
"""
def node_modules_paths(start):
  log('node_modules_paths: ', start)
  parts = split_path(start)
  i = len(parts) - 1
  dirs = []
  while i >= 0:
    if parts[i] is 'node_modules':
      i = i - 1
      continue

    _parts = (parts[:i + 1] + ['node_modules'])
    dir = os.path.join(*_parts)
    dirs.append(dir)
    i = i - 1
  return dirs

def split_path(start):
  path = os.path.normpath(start)

  drive, path_and_file = os.path.splitdrive(path)
  path, file = os.path.split(path_and_file)

  folders = [file]

  while 1:
    path, folder = os.path.split(path)

    if folder != "":
      folders.append(folder)
    else:
      if path != "":
        folders.append(path)

      break

  folders.reverse()

  parts = folders

  if (drive):
    parts = [drive] + parts

  return parts

# Run in terminal: node -pe "require('repl')._builtinLibs"
CORE_MODULES = [
  'assert',
  'buffer',
  'child_process',
  'cluster',
  'crypto',
  'dgram',
  'dns',
  'domain',
  'events',
  'fs',
  'http',
  'https',
  'net',
  'os',
  'path',
  'punycode',
  'querystring',
  'readline',
  'repl',
  'stream',
  'string_decoder',
  'tls',
  'tty',
  'url',
  'util',
  'v8',
  'vm',
  'zlib'
]