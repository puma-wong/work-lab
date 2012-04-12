#-*- coding: gbk -*-
import os
import sys
import datetime
from optparse import OptionParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib


SVN = "C:\Program Files\TortoiseSVN\bin\svn.exe"
if not os.path.exists(SVN): SVN = "svn.exe"
if os.name == "posix": SVN = "svn"

LOG = os.path.join(os.getcwd(), "log.txt")
RESULT = os.path.join(os.getcwd(), "result_design.html")

flag0 = "------------------------------------------------------------------------"
flag1 = "Changed paths:"

flag2 = "date: "
flag3 = "lines:"
flag4 = "-----------"
flag5 = "==========="
flag6 = "author: "
flag7 = "revision "

start_time = None
end_time = None
receivers = None
branch = None
svnurl = None

html = """
<HTML>
<HEAD>
	<META content="text/html; charset=gbk" http-equiv=Content-Type>
	<META name=GENERATOR content="MSHTML 8.00.6001.18854"><LINK rel=stylesheet 
	href="BLOCKQUOTE{margin-Top: 0px; margin-Bottom: 0px; margin-Left: 2em}">
</HEAD>
<BODY style="MARGIN: 10px; FONT-FAMILY: verdana; FONT-SIZE: 10pt">
<TABLE style="font-size: 10pt;" border="1" cellpadding="4" cellspacing="0">
	<TBODY>
	   <tr><td colspan="5" style="text-align: center; font-weight: bold;">$$BRANCH$$ 提交记录</td></tr>
	   <tr><td colspan="5" style="text-align: center;">统计时间段:$$FROM_TIME$$ 至 $$END_TIME$$</td></tr>
	   <tr><td>版本号</td><td>时间</td><td>文件</td><td>变更</td><td>提交注释</td></tr>
	   $$CONTENT$$
	</TBODY>
</TABLE> 
<br/>Note: A：增加；M：修改；C：冲突；D：删除；R：替换
</BODY>
<HR size=5 color="red"> 
</HTML>
"""

empty = """
<HTML>
<HEAD>
	<META content="text/html; charset=gbk" http-equiv=Content-Type>
	<META name=GENERATOR content="MSHTML 8.00.6001.18854"><LINK rel=stylesheet 
	href="BLOCKQUOTE{margin-Top: 0px; margin-Bottom: 0px; margin-Left: 2em}">
</HEAD>
<BODY style="MARGIN: 10px; FONT-FAMILY: verdana; FONT-SIZE: 10pt">
太好了,$$FROM_TIME$$ 至 $$END_TIME$$这段时间没人提交$$BRANCH$$分支的文件...
</BODY>
</HTML>
"""

commit_info_fmt = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
file_header_fmt = '<tr><th colspan="5" style="text-align: left; font-weight: bold;">%s</th></tr>'

def send_email(html_msg, receivers):
	ver = sys.version_info
	if ver[0] <= 2 and ver[1] <  5: return False

	msg = MIMEMultipart('related')
	msg['Subject'] = Header("svn提交记录通知", 'gbk')
	
	##发邮件的相关设定##
	msg['From'] = "someone@host"
	msg['To'] = receivers
	msgAlternative = MIMEMultipart('alternative')
	msg.attach(msgAlternative)
	msgText = MIMEText(html_msg, "html", "gbk")
	msgAlternative.attach(msgText)
	
	try:
		s = smtplib.SMTP("mail-host", 25)
		s.set_debuglevel(False)
		s.login("someone", "password")
		s.sendmail("someone@host", receivers.split(","), msg.as_string())
		s.quit()
		s.close()
	except:
		print "send failed"
		return False

	return True

def run_svnlog():
	global start_time, end_time, receivers, branch, svnurl
	parser = OptionParser()
	#parser.add_option("-w", "--workdir", dest="workdir", help="local code dir",)
	#parser.add_option("-a", "--author", dest="author", help="set filter for commitor",)
	#parser.add_option("-b", "--branch", dest="branch", help="set filter for branch",)
	parser.add_option("-s", "--starttime", dest="starttime", help="set date filter for start time",)
	parser.add_option("-e", "--endtime", dest="endtime", help="set date filter for end time",)
	#parser.add_option("-m", "--mail", dest="mail", help="set email address to receive the result, use ',' to split multiple address",)
	parser.add_option("-o", "--host", dest="host", help="set svn url",)
	
	(options, args) = parser.parse_args()
	#if options.mail: receivers = options.mail	

	if options.host: svnurl = options.host
        print svnurl
	cmd = '"%s" log %s'%(SVN, svnurl) 

	#if options.workdir:
	#	if os.path.exists(options.workdir):
	#		os.chdir(options.workdir)
	#	else:
	#		print "Err: %s is not a valid path"%(options.workdir)
	#		return False

	if options.starttime: start_time = "{"+options.starttime+"}"
	else:
		if int(datetime.datetime.today().strftime("%H")) >= 6:
			start_time = datetime.date.today().strftime("{%Y-%m-%d}")
		else:
			yesterday = datetime.date.today() - datetime.timedelta(1)
			start_time = yesterday.strftime("{%Y-%m-%d}")
	if options.endtime: end_time = "{"+options.endtime+"}"
	else: end_time = (datetime.datetime.today() + datetime.timedelta(1)).strftime("{%Y-%m-%d}")
	#if options.author: cmd += ' -w"%s"'%(options.author,)
	#if options.branch: branch = options.branch
	#else: branch = "HEAD"
	#cmd += ' -r"%s"'%(branch,)
	cmd += ' -r%s:%s -v > %s'%(start_time, end_time, LOG)
	print "running cmd: ", cmd
	cmd = '"%s"'%(cmd)
	if os.system(cmd): return False
	else: return True

def gene_html():
	if not os.path.exists(LOG): return False

	f = open(LOG)
	contents = []
	filename = ""
	msg = ""
	infos = []
	bFollowMsg = True
	ver_info = ""
	step = 0;
	action = ""
	for l in f:
		if l.startswith(flag0):
			step = 1
			if bFollowMsg:
                            	if len(ver_info) < 1: continue
        			contents.append(file_header_fmt%(ver_info))
                                infos.append(author)
                                infos.append(date)
                                infos.append(files)
                                infos.append(action)
        			infos.append(msg)
        			contents.append(commit_info_fmt%(infos[0], infos[1], infos[2], infos[3], infos[4]))
			msg = ""
			infos = []
			action = ""
		elif step == 1:
			#r24686 | wuw | 2011-01-10 11:54:51 +0800 (Mon, 10 Jan 2011) | 1 line
                        com_infos = l.split("|");
        		ver_info = com_infos[0].strip()[1:]
        		author = com_infos[1].strip()
        		date = com_infos[2][0:20].strip()

#可以指定只选取某人的提交信息##
#        		if cmp(author,"zhuli"):
#                                bFollowMsg = False
#                        else:
#                                bFollowMsg = True
			step = 2
		elif step == 2:
			files = ""
			step = 3
		elif step == 3:
			if len(l) < 2:
				step = 4
				continue
			action += l[3:4] + "<br/>"
			files += l[5:] + "<br/>"
		elif step == 4:
			if len(l) == 0: continue
			msg += l;
	f.close()
	
	if contents:
		tables = "\n		".join(contents)
		content = html.replace("$$CONTENT$$", tables)
		content = content.replace("$$FROM_TIME$$", start_time)
		content = content.replace("$$END_TIME$$", end_time)
		content = content.replace("$$BRANCH$$", svnurl)
	else:
		content = empty.replace("$$FROM_TIME$$", start_time)
		content = content.replace("$$END_TIME$$", end_time)
		content = content.replace("$$BRANCH$$", svnurl)

	return content

def main():
	if not run_svnlog():
		print "Err: run svn log error!"
		return
	
	print "do svn log query ok!"
	html_msg = gene_html()
	if receivers:
		send_email(html_msg, receivers)
		print "send result mail ok!"

	f = open(RESULT, "w")
	f.write(html_msg)
	f.close()

	if os.path.exists(LOG): os.remove(LOG)
	print "please open %s to see the result!"%(RESULT)

if __name__ == '__main__': 
	main()
