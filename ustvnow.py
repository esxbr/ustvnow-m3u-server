'''
    ustvnow

'''
import cookielib
import os
import re
import urllib, urllib2
import json
from xml.dom import minidom
from time import time
from datetime import datetime, timedelta

class Ustvnow:
	__BASE_URL = 'http://m.ustvnow.com'
	def __init__(self, user, password):
		self.user = user
		self.password = password
                    
	def get_channels(self, dologin=True):
		if dologin:
			self._login()

		content = self._get_json('gtv/1/live/listchannels', {'token': self.token})
		channels = []
		
		#print json.dumps(content);
   	
		results = content['results']['streamnames'];
    	
		for i in results:
			channels.append({
				'name': i['sname'], 
				'sname' : i['callsign'],
				'icon': self.__BASE_URL + '/' + i['img']
				})
    	
		return channels 
       
        
	def get_guide(self):
		self._login()
		content = self._get_json('gtv/1/live/channelguide', {'token': self.token})
		results = content['results'];

		now = time();

		doc = minidom.Document();
		base = doc.createElement('tv');
		base.setAttribute("cache-version", str(now));
		base.setAttribute("cache-time", str(now));
		base.setAttribute("generator-info-name", "IPTV Plugin");
		base.setAttribute("generator-info-url", "http://www.xmltv.org/");
		doc.appendChild(base)
		
		channels = self.get_channels(dologin=False);

		for channel in channels:
	
			name = channel['name'];
			id = channel['sname'];
		
			c_entry = doc.createElement('channel');
			c_entry.setAttribute("id", id);
			base.appendChild(c_entry)
		
		
			dn_entry = doc.createElement('display-name');
			dn_entry_content = doc.createTextNode(name);
			dn_entry.appendChild(dn_entry_content);
			c_entry.appendChild(dn_entry);
			
			dn_entry = doc.createElement('display-name');
			dn_entry_content = doc.createTextNode(id);
			dn_entry.appendChild(dn_entry_content);
			c_entry.appendChild(dn_entry);
			
			icon_entry = doc.createElement('icon');
			icon_entry.setAttribute("src", channel['icon']);
			c_entry.appendChild(icon_entry);
			
			
		for programme in results:
	
			start_time 	= datetime.fromtimestamp(float(programme['ut_start']));
			stop_time	= start_time + timedelta(seconds=int(programme['guideremainingtime']));
					
		
			pg_entry = doc.createElement('programme');
			pg_entry.setAttribute("start", start_time.strftime('%Y%m%d%H%M%S 0'));
			pg_entry.setAttribute("stop", stop_time.strftime('%Y%m%d%H%M%S 0'));
			pg_entry.setAttribute("channel", programme['callsign']);
			base.appendChild(pg_entry);
		
			t_entry = doc.createElement('title');
			t_entry.setAttribute("lang", "en");
			t_entry_content = doc.createTextNode(programme['title']);
			t_entry.appendChild(t_entry_content);
			pg_entry.appendChild(t_entry);
			
			st_entry = doc.createElement('sub-title');
			st_entry.setAttribute("lang", "en");
			st_entry_content = doc.createTextNode(programme['episode_title']);
			st_entry.appendChild(st_entry_content);
			pg_entry.appendChild(st_entry);
		
			d_entry = doc.createElement('desc');
			d_entry.setAttribute("lang", "en");
			d_entry_content = doc.createTextNode(programme['synopsis']);
			d_entry.appendChild(d_entry_content);
			pg_entry.appendChild(d_entry);
		
			dt_entry = doc.createElement('date');
			dt_entry_content = doc.createTextNode(start_time.strftime('%Y%m%d'));
			dt_entry.appendChild(dt_entry_content);
			pg_entry.appendChild(dt_entry);
		
			c_entry = doc.createElement('category');
			c_entry_content = doc.createTextNode(programme['xcdrappname']);
			c_entry.appendChild(c_entry_content);
			pg_entry.appendChild(c_entry);
			
			
			en_entry = doc.createElement('episode-num');
			en_entry.setAttribute('system', 'dd_progid');
			en_entry_content = doc.createTextNode(programme['content_id']);
			en_entry.appendChild(en_entry_content);
			pg_entry.appendChild(en_entry);
		
	
			i_entry = doc.createElement('icon');
			i_entry.setAttribute("src", self.__BASE_URL + '/' + programme['img']);
			pg_entry.appendChild(i_entry);
		
		return doc  

    
	def _build_url(self, path, queries={}):
		if queries:
			query = urllib.urlencode(queries)
			return '%s/%s?%s' % (self.__BASE_URL, path, query) 
		else:
			return '%s/%s' % (self.__BASE_URL, path)

	def _fetch(self, url, form_data=False):
		if form_data:
			req = urllib2.Request(url, form_data)
		else:
			req = url
		try:
			response = urllib2.urlopen(url)
			return response
		except urllib2.URLError, e:
			return False
        
	def _get_json(self, path, queries={}):
		content = False
		url = self._build_url(path, queries)

		response = self._fetch(url)
		if response:
			content = json.loads(response.read())
		else:
			content = False
        
		return content
		
	def _get_html(self, path, queries={}):
		html = False
		url = self._build_url(path, queries)

		response = self._fetch(url)
		if response:
			html = response.read()
		else:
			html = False

		return html
		
	#TODO this func
	def get_link(self, sname, quality=1, stream_type='rtmp'):
		self._login()
		
		self.__BASE_URL = 'http://lv2.ustvnow.com';
		html = self._get_html('iphone_ajax', {'tab': 'iphone_playingnow', 
											  'token': self.token})
		channel = re.search('class="panel".+?images\/' + sname + '.+?src="' + 
								'.+?".+?class="nowplaying_item">.+?' + 
								'<\/td>.+?class="nowplaying_itemdesc".+?' + 
								'<\/a>.+?<\/td>.+?href="(.+?)"', html, re.DOTALL);
		
		if channel == None:
			return None;
		
		url = channel.group(1);
		url = '%s%s%d' % (stream_type, url[4:-1], quality)
		
		return url    

	def _login(self):
		self.token = None
		self.cj = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        
		urllib2.install_opener(opener)
		url = self._build_url('gtv/1/live/login', {'username': self.user, 
                                               'password': self.password, 
                                               'device':'gtv', 
                                               'redir':'0'})
		response = self._fetch(url)
        #response = opener.open(url)
        
		for cookie in self.cj:
			print '%s: %s' % (cookie.name, cookie.value)
			if cookie.name == 'token':
				self.token = cookie.value
