import ustvnow
import sys
import os

def main(argv):

	username = 'xxxx@xxx.com';
	password = 'xxxx'

	ustv = ustvnow.Ustvnow(username, password)

	if argv[0] == 'channels':
		data = ustv.get_channels();
		
	if argv[0] == 'guide':
		data = ustv.get_guide();
		
	if argv[0] == 'link':
		data = ustv.get_link(argv[1], int(argv[2]));
		os.system('/Applications/VLC.app/Contents/MacOS/VLC ' + data);
		print data;
      	



if __name__ == "__main__":
   main(sys.argv[1:])