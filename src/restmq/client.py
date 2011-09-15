import sys
import simplejson
from twisted.web import client
from twisted.python import log
from twisted.internet import reactor, defer

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class CometClient(object):

	def __init__(self, queue_name, host="localhost", port=8888, protocol="http"):
		url = "%s://%s:%d/c/%s" % (protocol, host, port, queue_name)
		client.downloadPage(url, self)
		self.content_buffer = None

	def on_data(self, data):
		pass

	@defer.inlineCallbacks
	def write(self, content):

		# Sometimes when the queue is especially full the payload
		# won't be delivered entirely.
		if self.content_buffer:
			content = self.content_buffer.getvalue() + content

		for json in content.splitlines():
			try:
				qdata = simplejson.loads(json)
				data = simplejson.loads(qdata.get('value'))
			except Exception, e:
				if not self.content_buffer:
					self.content_buffer = StringIO()
				self.content_buffer.write(json)
				log.err("cannot decode json: %s" % str(e))
				yield
			else:
				self.content_buffer = None
				
				yield self.on_data(data)
				#return defer.maybeDeferred(self.on_data, data)
	
	def close(self):
		pass