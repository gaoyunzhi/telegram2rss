import cherrypy
import yaml
import os
from cherrypy.lib.static import serve_file

with open('CREDENTIALS') as f:
	CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)

class Rss(object):
	exposed = True
	def __init__(self):
		pass

	@cherrypy.popargs('rss_name')
	def GET(self, rss_name=None):
		filename = 'rss/' + rss_name
		return serve_file(os.path.abspath(filename))

	# HTML5 
	def OPTIONS(self):                                                      
		cherrypy.response.headers['Access-Control-Allow-Credentials'] = True
		cherrypy.response.headers['Access-Control-Allow-Origin'] = cherrypy.request.headers['ORIGIN']
		cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET'                                     
		cherrypy.response.headers['Access-Control-Allow-Headers'] = cherrypy.request.headers['ACCESS-CONTROL-REQUEST-HEADERS']

class Root(object):
	pass

root = Root()
root.rss = Rss()

conf = {
	'global': {
		'server.socket_host': '0.0.0.0',
		'server.socket_port': CREDENTIALS['port'],
	},
	'/': {
		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
	},
}
cherrypy.quickstart(root, '/', conf)
print(1)