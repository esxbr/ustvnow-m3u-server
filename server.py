import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import ustvnow
import SocketServer
import socket
import SimpleHTTPServer
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import base64

port = 8787;

class MyHandler(BaseHTTPRequestHandler):
 
    def do_HEAD(self):
    
		print 'do_HEAD path: ' + self.path;
		print 'do_HEAD query: ' + urlparse(self.path).query;
        
		self.send_response(200)

		if 'channels.m3u' in self.path:
			self.send_header('Content-type',	'application/x-mpegURL')
			
		elif self.path.startswith('/play'):
			self.send_header('Content-type',	'application/x-mpegURL')
			self.send_header('Accept-Ranges',	'none') # fix kodi bug
			
		elif 'epg.xml' in self.path:
			self.send_header('Content-type',	'txt/xml')
			
		else:
			self.send_header('Content-type',	'txt/html')

		self.end_headers()

    def do_GET(self):
       
        print 'do_GET path: ' + self.path;
        print 'do_GET query: ' + urlparse(self.path).query;
       
        args = parse_qs(urlparse(self.path).query);
        
        if 'u' in args and 'p' in args:
        	username = args['u'][0];
        	password = args['p'][0];
        	ustv = ustvnow.Ustvnow(username, password);
        	
        elif self.path.startswith('/play'):
        
        	args = parse_qs(base64.b64decode(self.path[5:]));
        	username = args['u'][0];
        	password = args['p'][0];
        	ustv = ustvnow.Ustvnow(username, password);
        	

        try:
            if 'channels.m3u' in self.path:

            	host = self.headers.get('Host');
            	quality = '1';
				
            	if 'q' in args != None and int(args['q'][0])>=1 and int(args['q'][0]) <=3:
					quality = args['q'][0];
            	
            	EXTM3U = "#EXTM3U\n";
            	
            	try:

					data = ustv.get_channels();

					for i in data:
						name 		= i["name"];
						icon 		= i["icon"];
				
						parameters = urllib.urlencode( { 
							'c' 		: name, 
							'i'			: icon, 
							'q' 		: quality, 
							'u'			: username, 
							'p'			: password } );
						
						EXTM3U += '#EXTINF:-1, tvg-name="' + name + '" tvg-logo="' + icon + '" group-title="Live", ' + name + '\n';
						EXTM3U += 'http://' + host + '/play'  + base64.b64encode(parameters) +'\n\n';
						
						#print 'http://' + host + '/play'  + base64.b64encode(parameters);
					
            	except Exception as e:
						EXTM3U += '#EXTINF:-1, tvg-id="Error" tvg-name="Error" tvg-logo="" group-title="Error", ' + str(e) + '\n';
						EXTM3U += 'http://\n\n';
        	
        	
                self.send_response(200)
                self.send_header('Content-type',	'application/x-mpegURL')
                self.send_header('Connection',	'close')
                self.send_header('Content-Length', len(EXTM3U))
                self.end_headers()
                self.wfile.write(EXTM3U.encode('utf-8'))
                                
            elif self.path.startswith('/play'):
				
				channel = args['c'][0];
				quality = args['q'][0];
				icon = args['i'][0];


				url = ustv.get_link(channel, int(quality));
				
				print url;
				
				self.send_response(301)
				self.send_header('Location',	url)
				self.end_headers()
				
				                
            elif 'epg.xml' in self.path:
            
				
				try:
					data = ustv.get_guide();
					xml = data.toxml(encoding='utf-8');
				except Exception as e:
					xml  = '<?xml version="1.0" encoding="ISO-8859-1"?>'
					xml += '<error>' + str(e) + '</error>';
					
				
				self.send_response(200)
				self.send_header('Content-type',	'txt/xml')
				self.send_header('Connection',	'close')
				self.send_header('Content-Length', len(xml))
				self.end_headers()
				self.wfile.write(xml)
				                 
            elif 'stop' in self.path:
				msg = 'Stopping ...';
            	
				self.send_response(200)
				self.send_header('Content-type',	'text/html')
				self.send_header('Connection',	'close')
				self.send_header('Content-Length', len(msg))
				self.end_headers()
				self.wfile.write(msg.encode('utf-8'))
                
				server.socket.close();
                
            elif 'online' in self.path:
				msg = 'Yes. I am.';
            	
				self.send_response(200)
				self.send_header('Content-type',	'text/html')
				self.send_header('Connection',	'close')
				self.send_header('Content-Length', len(msg))
				self.end_headers()
				self.wfile.write(msg.encode('utf-8'))

            
            else:
            	self.send_error(400,'Bad Request');
            	
        except IOError:
            self.send_error(500,'Internal Server Error ' + str(IOError))




def startServer():
	global port;
	

	try:
		server = SocketServer.TCPServer(('', port), MyHandler);
		server.serve_forever();
		
	except KeyboardInterrupt:
		if server != None:
			server.socket.close();


if __name__ == '__main__':
	startServer();
	

        

