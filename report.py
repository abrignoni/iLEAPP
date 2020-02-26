import glob
import os
import os.path
import pathlib
import re
import shutil
import sqlite3
import sys
from time import process_time


def report(reportfolderbase, time, extracttype, pathto):
	os.mkdir(reportfolderbase+'/_elements')

	abr = os.path.dirname(os.path.abspath(__file__))
	sidebartop = ''' <!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN' 'http://www.w3.org/TR/html4/loose.dtd'>
	<html>
	<head>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
	<link rel='stylesheet' type='text/css' href='report.css'>
	<title>osTriage report menu</title>
	</head>
	<style> a {   
			color: blue;   
		}

		a[tabindex]:focus {
			color:red;
			outline: none;
		}
	</style>
	<body class='menuBackground'>
	<div class='menuBackgroundOverlay'>'''

	filedatahtml = open(reportfolderbase+'/_elements/sidebar.html', mode='a+')
	filedatahtml.write(sidebartop)

	x = sorted(next(os.walk(reportfolderbase))[1])
	control = (x[0])

	filedatahtml.write('<div id="button">')
	filedatahtml.write(f'<div id="menuSub">{control}</div>')
	filedatahtml.write('<ul>')

	mib = ['Apps_Historical', 'Apps_State', 'System_State']
	notification12 = 0
	notification11 = 0
	
	for root, dirs, files in sorted(os.walk(reportfolderbase)):
		for file in files:
			if file.endswith(".html"):	
				fullpath = (os.path.join(root, file))
				head, tail = os.path.split(fullpath)
				p = pathlib.Path(fullpath)
				SectionHeader = (p.parts[-2])
				HtmlFilePath = p		
				if 'iOS 12 Notifications' in fullpath:
					if notification12 == 0 and tail == 'iOS12_Notifications.html':
						notification12 = 1
						filedatahtml.write('</ul>')
						filedatahtml.write('</div>')
						filedatahtml.write('<div id="button">')
						filedatahtml.write(f'<div id="menuSub">iOS 12+ Notifications</div>')
						filedatahtml.write('<ul>')
						filedatahtml.write(f'<li class="ios12" ><a href="../{SectionHeader}/{tail}" tabindex="1" target="content">{SectionHeader}</a></li>')
					else:
						pass		
				elif 'iOS 11 Notifications' in fullpath:
					if notification11 == 0:
						notification11 = 1
						filedatahtml.write('</ul>')
						filedatahtml.write('</div>')
						filedatahtml.write('<div id="button">')
						filedatahtml.write(f'<div id="menuSub">iOS 11 Notifications</div>')
						filedatahtml.write('<ul>')
						filedatahtml.write(f'<li class="ios11" ><a href="../{SectionHeader}/{tail}" tabindex="1" target="content">{SectionHeader}</a></li>')
					else:
						filedatahtml.write(f'<li class="ios11" ><a href="../{SectionHeader}/{tail}" tabindex="1" target="content">{SectionHeader}</a></li>')
				elif SectionHeader == '_elements':
					pass
				elif SectionHeader in mib:
					if control == SectionHeader:
						filedatahtml.write(f'<li class="{SectionHeader}" ><a href="../Mobile_Installation_Logs/{SectionHeader}/{tail}" target="content"> {tail}</a></li>')
					else:
						control = SectionHeader
						filedatahtml.write('</ul>')
						filedatahtml.write('</div>')
						filedatahtml.write('<div id="button">')
						filedatahtml.write(f'<div id="menuSub">{SectionHeader}</div>')
						filedatahtml.write('<ul>')
						filedatahtml.write(f'<li class="{SectionHeader}" ><a href="../Mobile_Installation_Logs/{SectionHeader}/{tail}" target="content"> {tail}</a></li>')
				else:
					if control == SectionHeader:
						filedatahtml.write(f'<li class="{SectionHeader}" ><a href="../{SectionHeader}/{tail}" tabindex="1" target="content"> {tail}</a></li>')
						#print(fullpath)
					else:
						control = SectionHeader
						filedatahtml.write('</ul>')
						filedatahtml.write('</div>')
						filedatahtml.write('<div id="button">')
						filedatahtml.write(f'<div id="menuSub">{SectionHeader}</div>')
						filedatahtml.write('<ul>')
						filedatahtml.write(f'<li class="{SectionHeader}" ><a href="../{SectionHeader}/{tail}" tabindex="1" target="content"> {tail}</a></li>')
				
	filedatahtml.write('</ul>')
	filedatahtml.write('</div>')
	filedatahtml.write('<br>')				
	filedatahtml.close()				
	#create report index.html
	fullpage = ''' <!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN' 'http://www.w3.org/TR/html4/loose.dtd'>
	<html>
	<head>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
	<title>iLEAPP report</title>
	<link rel='stylesheet' type='text/css' href='_meta/report.css'>
	</head>
	<frameset rows='120,*'>
	<frame name='topNav'    src='_elements/top.html'  frameborder='no'>
	<frameset cols='220,*'>
	<frame name='menu'    src='_elements/sidebar.html'    scrolling='auto' noresize frameborder='no'>
	<frame name='content' src='_elements/data.html' scrolling='auto' noresize frameborder='no'>
	</frameset>
	</frameset>
	<noframes>
	Your browser does not support frames, and therefore is unable to view this iLEAPP report.  Please update your browser.  If you believe this message to be in error, please contact the program author.
	</noframes>
	</html>'''

	filedatahtml = open(reportfolderbase+'/index.html', mode='a+')
	filedatahtml.write(fullpage)
	filedatahtml.close()

	fulltop = '''<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN' 'http://www.w3.org/TR/html4/loose.dtd'>
	<html>
	<head>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
	<link rel='stylesheet' type='text/css' href='report.css'>
	<title>iLEAPP report</title>
	</head>
	<body>
	<div class='header_logo'><img src='logo.jpg' width='95' height='95' alt='logo'></div>
	<div class='header_txt'>iOS Logs Events And Properties Parser
	</div>
	</body>
	</html>
	'''

	filedatahtml = open(reportfolderbase+'/_elements/top.html', mode='a+')
	filedatahtml.write(fulltop)
	filedatahtml.close()

	fulldata = '''<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN' 'http://www.w3.org/TR/html4/loose.dtd'>
	<html>
	<head>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
	<title>iLEAPP content</title>
	<link rel='stylesheet' type='text/css' href='report.css'>
	</head>
	<body>
	<h1>iLEAPP 1.0 report</h1>
	<hr>
	<h2>Case </h2>
	<table width='750' border='0'>
	
	'''
	time = str(abs(time))
	filedatahtml = open(reportfolderbase+'/_elements/data.html', mode='a+')
	filedatahtml.write(fulldata)
	filedatahtml.write(f'<tr><td>Extraction location: </td><td>{pathto}</td></tr>')
	filedatahtml.write(f'<tr><td>Extraction type: </td><td>{extracttype}</td></tr>')
	filedatahtml.write(f'<tr><td>Report directory: </td><td>{reportfolderbase}</td></tr>')
	filedatahtml.write(f'<tr><td>Processing in secs: </td><td>{time}</td></tr>')
	filedatahtml.write('</table><br>')
	
	if os.path.isfile(reportfolderbase+'Device Info/di.db'):
		db = sqlite3.connect(reportfolderbase+'Device Info/di.db')
		cursor = db.cursor()
		cursor.execute('''SELECT
		* from devinf 
		order by ord asc
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			filedatahtml.write(f'<h2>Device Info</h2>')
			filedatahtml.write('<table width="750" border="0">')			
			for row in all_rows:
				filedatahtml.write(f'<tr><td>{row[1]}</td><td>{row[2]}</td></tr>')
			filedatahtml.write(f'</table><br>')
			

	
	
	filedatahtml.write('<h2>Informational</h2>')
	filedatahtml.write('<table width="750" border="0">')
	#filedatahtml.write('<tr>')
	filedatahtml.write(f'<tr><td>Blog: </td><td><a href="https://abrignoni.com" target=”_blank”>abrignoni.com</a></td></tr>')
	filedatahtml.write(f'<tr><td>Github: </td><td><a href="https://github.com/abrignoni" target=”_blank”>github.com/abrignoni</a></td></tr>')
	filedatahtml.write(f'<tr><td>Twitter: </td><td><a href="https://twitter.com/AlexisBrignoni" target=”_blank”>@AlexisBrignoni</a></td></tr>')
	filedatahtml.write('</table><br>')
	filedatahtml.write('<h2>About</h2>')
	filedatahtml.write('<table width="750" border="0">')
	#filedatahtml.write('<tr>')
	filedatahtml.write(f'<tr><td>Artifact references: </td><td><a href="https://abrignoni.com" target=”_blank”>Pending</a></td></tr>')
	filedatahtml.write(f"<tr><td>Awesome Friends: </td><td><a href='https://abrignoni.blogspot.com/2020/01/awesome-friends.html' target='_blank'>Contributors I can't thank enough.</a></td></tr>")
	filedatahtml.write('</table><br></body></html>')
	filedatahtml.close()

	shutil.copy2('logo.jpg', reportfolderbase+'/_elements/')
	shutil.copy2('report.css', reportfolderbase+'/_elements/')


