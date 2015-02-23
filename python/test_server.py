from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import MySQLdb as mysql
import random
import time
import cgi

class datastoreHandler:
	# Assuming we have this database
	#
	#  CREATE TABLE images (p_id MEDIUMINT NOT NULL AUTO_INCREMENT, url_unique VARCHAR(2084) NOT NULL, datetime DATETIME NOT NULL, PRIMARY KEY (p_id))
	#

	def __init__(self, database = None):
		# NOTE(jsalem): Change calues here to point script at different mysqldb
		self.dbConn = mysql.connect(host="localhost", user="testadmin", passwd="password", db=database)
		return

	def addImgUrl (self, imageurl = None, datetime = None):
		if (imageurl != None and datetime != None):
			create = "CREATE TABLE IF NOT EXISTS images \
					  (p_id MEDIUMINT NOT NULL AUTO_INCREMENT, \
					  url_unique VARCHAR(2084) NOT NULL, \
					  datetime DATETIME NOT NULL, \
					  PRIMARY KEY (p_id))"
			c = self.dbConn.cursor()
			c.execute(create)
			c.close()

			stmt = "INSERT INTO images (url_unique, datetime) VALUES ('%s', '%s')" % (imageurl, datetime)
			# DEBUG(jsalem)
			# print "======="
			# print stmt
			# print "======="
			c = self.dbConn.cursor()
			c.execute(stmt)
			c.close()
			self.dbConn.commit()
		return

	def getLongestUrl (self):
		qry = "SELECT url_unique FROM images ORDER BY length(url_unique) DESC LIMIT 1"
		c = self.dbConn.cursor()
		c.execute(qry)
		ret = c.fetchone()
		c.close()
		return ret[0]

	def getRandomUrl (self):
		# get num of records
		count_stmt = "SELECT COUNT(url_unique) FROM images"
		c = self.dbConn.cursor()
		c.execute(count_stmt)
		count = c.fetchone()
		c.close()

		rand = random.randint(1,count[0])
		rand_stmt = "SELECT url_unique FROM images WHERE p_id <= %d AND p_id >= %d" % (rand, rand)
		c = self.dbConn.cursor()
		c.execute(rand_stmt)
		ret = c.fetchone()
		c.close()
		return ret[0]


## HTTP POST request
##
## imageurl = "http://g.com/g.png"
## datetime = "12-03-2015 4:50"
##
## NOTE(jsalem): These are the only fields accepted in this script. Alternatively,
##				 you could take just the imageurl and generate the timestamp server-side
##				 with the following snippet:
##
##				 datetime = time.strftime('%Y-%m-%d %H:%M:%S')
##

class Handler(BaseHTTPRequestHandler):

	handler = datastoreHandler("test_dev")

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write('GET Request\n')
		self.wfile.write(self.path)
		self.wfile.write('\n')
		if self.path == '/rand':
			random = self.handler.getRandomUrl()
			self.wfile.write(random)
			self.wfile.write('\n')
		if self.path == '/longest':
			longest = self.handler.getLongestUrl()
			self.wfile.write(longest)
			self.wfile.write('\n')
		return

	def do_POST(self):
        # Get form data
		form = cgi.FieldStorage(fp=self.rfile,
            					headers=self.headers,
            					environ={'REQUEST_METHOD':'POST',
                     			'CONTENT_TYPE':self.headers['Content-Type'],
                     			})
        # Response
		self.send_response(200)
		self.end_headers()
		# echo form data back to client
		for field in form.keys():
			self.wfile.write('\t%s = %s\n' % (field, form[field].value))
		if "imageurl" not in form.keys() or "datetime" not in form.keys():
			print "<H1>Error</H1>"
			print "Please fill in the imageurl and datetime fields."
			return
		self.handler.addImgUrl(imageurl = form['imageurl'].value, datetime = form['datetime'].value)
		return


if __name__ == '__main__':
	# NOTE(jsalem): change server host here
	server = HTTPServer(('localhost', 8080), Handler)
	print "server started..."
	server.serve_forever()
