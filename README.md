# Local-Server
python implementation of a simple web server

files in 'files' directory represent web pages (url is according to file path excluding 'files').
script recieves requested port as execution argument.

**Running instructions:** run the script and access server through web browser by entering the URL:

\<serverIP>:\<serverPORT>/\<filePath>
for example: 127.0.0.1:5402/c/home.html

if no filepath is givn, server will open 'index.html' page.
if the filepath given is 'redirect.html', server will return 301 code redirecting to 'result.index'
