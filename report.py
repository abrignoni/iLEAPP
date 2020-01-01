import sys, os, re, glob, pathlib, shutil
from time import process_time

def report(reportfolderbase):
	os.mkdir(reportfolderbase+'/_elements')

	abr = os.path.dirname(os.path.abspath(__file__))
	sidebartop = ''' <!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN' 'http://www.w3.org/TR/html4/loose.dtd'>
	<html>
	<head>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
	<link rel='stylesheet' type='text/css' href='report.css'>
	<title>osTriage report menu</title>
	</head>
	<body class='menuBackground'>
	<div class='menuBackgroundOverlay'>'''

	filedatahtml = open(reportfolderbase+'/_elements/sidebar.html', mode='a+')
	filedatahtml.write(sidebartop)

	x = sorted(next(os.walk(reportfolderbase))[1])
	control = (x[0])

	filedatahtml.write('<div id="button">')
	filedatahtml.write(f'<div id="menuSub">{control}</div>')
	filedatahtml.write('<ul>')

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
						filedatahtml.write('<br>')
						filedatahtml.write('<div id="button">')
						filedatahtml.write(f'<div id="menuSub">iOS 12+ Notifications</div>')
						filedatahtml.write('<ul>')
						filedatahtml.write(f'<li class="ios12" ><a href="{abr}/{HtmlFilePath}" target="content">{SectionHeader}</a></li>')
					else:
						pass		
				elif 'iOS 11 Notifications' in fullpath:
					if notification11 == 0:
						notification11 = 1
						filedatahtml.write('</ul>')
						filedatahtml.write('</div>')
						filedatahtml.write('<br>')
						filedatahtml.write('<div id="button">')
						filedatahtml.write(f'<div id="menuSub">iOS 11 Notifications</div>')
						filedatahtml.write('<ul>')
						filedatahtml.write(f'<li class="ios11" ><a href="{abr}/{HtmlFilePath}" target="content">{SectionHeader}</a></li>')
					else:
						filedatahtml.write(f'<li class="ios11" ><a href="{abr}/{HtmlFilePath}" target="content">{SectionHeader}</a></li>')
				elif SectionHeader == '_elements':
					pass
				else:
					if control == SectionHeader:
						filedatahtml.write(f'<li class="{SectionHeader}" ><a href="{abr}/{HtmlFilePath}" target="content">{tail}</a></li>')
						#print(fullpath)
					else:
						control = SectionHeader
						filedatahtml.write('</ul>')
						filedatahtml.write('</div>')
						filedatahtml.write('<br>')
						filedatahtml.write('<div id="button">')
						filedatahtml.write(f'<div id="menuSub">{SectionHeader}</div>')
						filedatahtml.write('<ul>')
						filedatahtml.write(f'<li class="{SectionHeader}" ><a href="{abr}/{HtmlFilePath}" target="content">{tail}</a></li>')
				
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
	<h2>Case information</h2>
	<table width='750' border='0'>
	<tr>
	</tr>
	</table>
	<br>
	</body>
	</html>'''
	filedatahtml = open(reportfolderbase+'/_elements/data.html', mode='a+')
	filedatahtml.write(fulldata)
	filedatahtml.close()

	shutil.copy2('logo.jpg', reportfolderbase+'/_elements/')
	shutil.copy2('report.css', reportfolderbase+'/_elements/')


