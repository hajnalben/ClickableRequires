import sublime
import sublime_plugin
import os
import json
import webbrowser

DEBUG = True
REGEXP = 'require\(.*?\)'

def log(str):
  if DEBUG: print(str)

# The pseudocode of require: https://nodejs.org/api/modules.html#modules_all_together
class OpenRequireUnderCursorCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    require_statements = self.view.find_all(REGEXP)
    cursor_position = self.view.sel()[0]

    for require_statement in require_statements:
      if cursor_position.intersects(require_statement):
        statement = self.view.substr(require_statement)

        # Removes the "require('" and "')" strings to have only the package name
        module = statement[9:-2]
        self.open_node_module(module)

  def open_node_module(self, module):
    window = self.view.window()
    ctx = window.extract_variables()
    file_path = ctx['file_path']

    if module in core_modules:
      return webbrowser.open('https://nodejs.org/api/' + module + '.html', autoraise=True)
    elif module.startswith('.'):
      path = file_path + '/' + module
      file = self.load_as_file(path) or self.load_as_directory(path)
    else:
      file = self.load_node_modules(module, file_path)

    if file:
      window.open_file(file)
      ## TODO: Make it optional
      sublime.set_timeout(lambda: window.run_command('reveal_in_side_bar'), 100)

  """
  LOAD_AS_FILE(X)
    1. If X is a file, load X as JavaScript text.  STOP
    2. If X.js is a file, load X.js as JavaScript text.  STOP
    3. If X.json is a file, parse X.json to a JavaScript Object.  STOP
    4. If X.node is a file, load X.node as binary addon.  STOP
  """
  def load_as_file(self, path):
    log('load_as_file: ' + path)
    if os.path.isfile(path):
      return path
    elif os.path.isfile(path + '.js'):
      return path + '.js'
    elif os.path.isfile(path + '.json'):
      return path + '.json'
    elif os.path.isfile(path + '.node'):
      return path + '.node'

  """
  LOAD_AS_DIRECTORY(X)
    1. If X/package.json is a file,
       a. Parse X/package.json, and look for "main" field.
       b. let M = X + (json main field)
       c. LOAD_AS_FILE(M)
       d. LOAD_INDEX(M)
    2. LOAD_INDEX(X)
  """
  def load_as_directory(self, path):
    log('load_as_directory: ' + path)
    if os.path.exists(path + '/package.json'):
      package_json = json.load(open(path + '/package.json', 'r', encoding='UTF-8'))
      if package_json['main']:
        main_path = path + '/' + package_json['main']
        return self.load_as_file(main_path) or self.load_index(main_path)
    else:
      return self.load_index(path)

  """
  LOAD_INDEX(X)
    1. If X/index.js is a file, load X/index.js as JavaScript text.  STOP
    2. If X/index.json is a file, parse X/index.json to a JavaScript object. STOP
    3. If X/index.node is a file, load X/index.node as binary addon.  STOP
  """
  def load_index(self, path):
    log('load_index: ' + path)
    if os.path.exists(path + '/index.js'):
      return path + '/index.js'
    elif os.path.exists(path + '/index.json'):
      return path + '/index.json'
    elif os.path.exists(path + '/index.node'):
      return path + '/index.node'

  """
  LOAD_NODE_MODULES(X, START)
    1. let DIRS=NODE_MODULES_PATHS(START)
    2. for each DIR in DIRS:
       a. LOAD_AS_FILE(DIR/X)
       b. LOAD_AS_DIRECTORY(DIR/X)
  """
  def load_node_modules(self, module, start):
    log('load_node_modules: ' + module + ' - ' + start)
    dirs = self.node_modules_paths(start)
    for dir in dirs:
      file = self.load_as_file(dir + '/' + module) or self.load_as_directory(dir + '/' + module)
      if file:
        return file

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
  def node_modules_paths(self, start):
    log('node_modules_paths: ' + start)
    parts = start.split('/')
    i = len(parts) - 1
    dirs = []
    while i >= 0:
      dir = '/'.join(parts[:i]) + '/node_modules'
      dirs.append(dir)
      i = i - 1
    return dirs

core_modules = [
    'assert',
    'buffer',
    'cluster',
    'child_process',
    'crypto',
    'dgram',
    'dns',
    'domain',
    'events',
    'fs',
    'http',
    'https',
    'net',
    'npm',
    'os',
    'path',
    'punycode',
    'readline',
    'stream',
    'string_decoder',
    'tls',
    'url',
    'util',
    'vm',
    'zlib'
]