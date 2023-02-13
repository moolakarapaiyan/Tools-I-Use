from flask import Flask, render_template,send_file,redirect, url_for, request, session,jsonify
import subprocess
import time
import glob
import psutil
import socket
from urllib.parse import urlparse
from yattag import Doc, indent
from http_request import HTTPRequest
from html import unescape
import os

app = Flask(__name__)

def stopme():
    if (isrunning() == "yes"):
        os.system("ps -C proxify -o pid=|xargs kill -9 > /dev/null 2>&1")
    else:
        return render_template("json.html")
        
   
    
#rendering the HTML page which has the button
@app.route('/')
def json():
    return render_template('json.html')

@app.route('/status', methods=['GET', 'POST'])
def isrunning():
    procsName = []
    for proc in psutil.process_iter(['name']):
            procsName.append(proc.info)
    if "proxify" in str(procsName):
        return "yes"
    else:
        return "no"
    
        
#background process happening without any refreshing
@app.route('/background_process_start',methods=['GET', 'POST'])
def background_process_start():
    global setterName
    global scan_FileName
    name = request.form.get('name')
    setterName = name
    scan_FileName = time.strftime('%m-%d-%Y-%H:%M:%S',time.gmtime()) + "_" + setterName+".xml"
    if(isrunning() == "yes"):
        return render_template("json.html")
    else:
        
        print("proxyify started........")
        cmd = ['proxify', '-dump-req','-silent']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for line in p.stdout:
            print(line)
        p.wait()
        print(p.returncode)
    
        return render_template("json.html")

@app.route('/background_process_stop',methods=['GET', 'POST'])
def background_process_stop():
    if (isrunning() == "yes"):
        stopme()
        print("Proxy Stopped......")
        main()
        return redirect("/scanned", code=302)
    else:
        return render_template("json.html")
        
        
@app.route('/installation-guide',methods=['GET', 'POST'])
def installation():
    return render_template('/install.html')
    
   
@app.route('/scans/<path:filename>',methods = ['GET','POST'])
def downloadFile (filename):
   
    path = os.getcwd()+"/scans/"+filename
    filesize = os.path.getsize(filename)
    print(path)
    if(os.path.exists(path)):
        return send_file(path, as_attachment=True)
    else:
        return send_file(path, as_attachment=True)

@app.route('/cert/<path:filename>',methods = ['GET','POST'])
def certdownload (filename):
   
    path = os.getcwd()+"/cert/"+filename
    if(os.path.exists(path)):
        return send_file(path, as_attachment=True)
    else:
        return send_file(path, as_attachment=True)
        
@app.route('/scanned',methods = ['GET','POST'])
def table():
    dir_name = 'scans/'
# Get list of all files only in the given directory
    list_of_files = filter( os.path.isfile,glob.glob(dir_name + '*') )
    data = {time.strftime('%m-%d-%Y-%H:%M:%S',time.gmtime(os.path.getmtime(file_path))) : file_path for file_path in list_of_files } 
    reversed_data = dict(reversed(list(data.items())))
    headings = ("Timestamp","File", "FileSize") 
    return render_template("table.html",headings = headings,data = reversed_data)

def xml_maker(requestobj,raw_http_request):
    global scanner_host
    headers,data,method,request,uri,port,protocol,host,ipAdd,extension = parser(requestobj)
    scanner_host = host
    doc, tag, text = Doc().tagtext()
    #with tag('items'):
    with tag('item'):
        with tag('url'):
            text("<![CDATA["+protocol+"://"+host+uri+"]]>")
        with tag('host', ip=ipAdd):
            text(host)
        with tag('port'):
            text(port)
        with tag("protocol"):
            text(protocol)
        with tag('method'):
            text("<![CDATA["+method+"]]>")
        with tag("path"):
            text("<![CDATA["+uri+"]]>")
        with tag("extension"):
            text(extension)
        with tag('request',base64="false"):
            text("<![CDATA["+raw_http_request+"]]>")

    result = indent(
        doc.getvalue(),
        indentation = ' '*4,
        newline = '\r\n'
    )
    
    xml_file = open("scans/"+scan_FileName, "a")
    xml_file.write(unescape(result))
    xml_file.close()



def parser(request):
    
    parsed_url = urlparse(request.path)
    host_header_value = request.headers.get('host', None)
    scheme = parsed_url.scheme
    port = parsed_url.port
    head = request.headers
    host = head['Host']
    ip = socket.gethostbyname(host)
    port = "443"
    protocol = "https"
    extension="null"
   
    parsed_url = urlparse(request.path)
        
    request.path = parsed_url.path
    if parsed_url.query:
        request.path += '?{}'.format(parsed_url.query) 

   
    headers=request.headers
    data=request.data
    cookies=request.cookies
    method=request.command
    uri=request.path
    host=host
    port=port
    
    return headers,data,method,request,uri,port,protocol,host,ip,extension


def main():
    header="""<?xml version=\"1.1\"?>
<!DOCTYPE items [
<!ELEMENT items (item*)>
<!ATTLIST items burpVersion CDATA \"\">
<!ATTLIST items exportTime CDATA \"\">
<!ELEMENT item (time, url, host, port, protocol, method, path, extension, request, status, responselength, mimetype, response, comment)>
<!ELEMENT time (#PCDATA)>
<!ELEMENT url (#PCDATA)>
<!ELEMENT host (#PCDATA)>
<!ATTLIST host ip CDATA \"\">
<!ELEMENT port (#PCDATA)>
<!ELEMENT protocol (#PCDATA)>
<!ELEMENT method (#PCDATA)>
<!ELEMENT path (#PCDATA)>
<!ELEMENT extension (#PCDATA)>
<!ELEMENT request (#PCDATA)>
<!ATTLIST request base64 (true|false) \"false\">
<!ELEMENT status (#PCDATA)>
<!ELEMENT responselength (#PCDATA)>
<!ELEMENT mimetype (#PCDATA)>
<!ELEMENT response (#PCDATA)>
<!ATTLIST response base64 (true|false) \"false\">
<!ELEMENT comment (#PCDATA)>
]>
<items burpVersion=\"2022.3.9\" exportTime=\"Wed Jul 06 16:30:50 UTC 2022\">
"""
    
    xml_file = open("scans/"+scan_FileName, "a")
    xml_file.write(header)
    xml_file.close()

    filelist = [f for f in glob.glob("logs/*.txt")]
    file_list = [s for s in filelist if "jetblue.com" or "b6orgeng.net" in s]

    try:
        for files in file_list:
            raw_http_request = ''.join(open(files, 'r').readlines())
            request = HTTPRequest(raw_http_request)
            if request:
                xml_maker(request,raw_http_request)
    
        xml_file = open("scans/"+scan_FileName, "a")
        xml_file.write("\n</items>")
        xml_file.close()
    except:
        pass
if __name__ == '__main__':
    app.run(debug=True)
