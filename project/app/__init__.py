from flask import Flask

# Startup stuff
app = Flask(__name__)
app.config.from_object('config')

# Jinja initialization to use PyJade
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

# Global jinja functions
app.jinja_env.globals.update(str=str)
app.jinja_env.globals.update(enumerate=enumerate)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(int=int)
app.jinja_env.globals.update(getattr=getattr)
app.jinja_env.globals.update(hasattr=hasattr)
app.jinja_env.globals.update(isinstance=isinstance)
app.jinja_env.globals.update(type=type)
app.jinja_env.globals.update(dict=dict)
app.jinja_env.globals.update(list=list)
app.jinja_env.globals.update(tuple=tuple)
app.jinja_env.globals.update(zip=zip)

# Import routes
from app import single, multiple

app.register_blueprint(single.bp)
app.register_blueprint(multiple.bp)
