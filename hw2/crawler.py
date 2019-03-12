import urllib.request
from html.parser import HTMLParser
import sys
if len(sys.argv) < 3:
    print("Error: Need arguments username and password to crawl")
    exit()

username = sys.argv[1]
password = sys.argv[2]
#assumption: host is always on neu servers and this url given by project
host = "http://cs5700f18.ccs.neu.edu/"
def fullUrl(path):
    return "{}{}".format(host, path)

#handles the html tags and puts them in a list with attributes
class MyHTMLParser(HTMLParser):
    tags = []
    data = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, attrs))
    def handle_startendtag(self,startendTag, attrs):
        self.tags.append((startendTag, attrs))
    def handle_data(self, data):
        #the only data we are interested in is the flag
        if data.startswith('FLAG'):
            self.data.append(data)
    def clear(self):
        self.tags = []
        self.data = []

    

page = urllib.request.urlopen(fullUrl("accounts/login/?next=/fakebook/"))
parser = MyHTMLParser()
page = str(page.read())
parser.feed(page)

#Any values needed for a request ie form values or sessionid
values = {
    'username' : username,
    'password' : password,
    'csrfmiddlewaretoken': '',
    'next' : '/fakebook/'
}
#the csrf token is in a hidden input field so we have to go through all the input tags
for tag in parser.tags:
    if tag[0] == 'input':
        attrs = tag[1]
        if attrs[0][1] == "\\'hidden\\'":
            values['csrfmiddlewaretoken'] = attrs[-1][1][2:-2]

#when logging in the login requests returns a 302 redirect. That redirect has the sessionid
#we need to redirect to the new url but also update our cookies to use the session id
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        cookies = req.get_header('Cookie')
        sessionId = headers['Set-Cookie'][0:headers['Set-Cookie'].index(";")]
        values["sessionId"] = sessionId
        req.add_header('Cookie', cookies + ";" + sessionId)
        req.full_url = newurl
        return req 

opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

headers = {'Content-Type' : "application/x-www-form-urlencoded", 'Cookie': "csrftoken={}".format(values['csrfmiddlewaretoken'])}
data = urllib.parse.urlencode(values).encode()
req = urllib.request.Request(fullUrl("accounts/login/?next=/fakebook/"), data, headers, method='POST')
response = urllib.request.urlopen(req)
#if username and password are incorrect
if values.get('sessionId', None) == None:
    print("Error: incorrect username and password")
    exit()

frontier = ["fakebook/"]
visited = {}
parser.clear()
header = {'Cookie': "csrftoken={};{}".format(values['csrfmiddlewaretoken'], values['sessionId'])}
flags = []
retry = 0
#main crawler loop
while len(frontier) != 0 and len(flags) != 5:
    url = frontier[0]
    if visited.get(url, False):
        frontier.pop(0)
        continue
    req = urllib.request.Request(fullUrl(url), headers=header)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        #for a 500 we have to retry
        if e.code == 500:
            #only retry a url 3 times to avoid infinite retrying
            if retry == 3:
                frontier.pop(0)
                visited[url] = True
            retry += 1
            continue
        #for a 403/404 abandon url
        if e.code == 403 or e.code == 404:
            frontier.pop(0)
            visited[url] = True
            continue
    except urllib.error.URLError as e:
        continue
    retry = 0
    parser.clear()
    parser.feed(str(response.read()))
    visited[url] = True
    frontier.pop(0)
    for tag in parser.tags:
        #gather all links
        if tag[0] == 'a':
            attrs = tag[1]
            #href is the first attribute
            url = attrs[0][1]
            if url[0] == "/":
                url = url[1:]
            if 'fakebook' in url and not visited.get(url, False):
                frontier.append(url)
        #check for secret flag in the form <h2 class='secret_flag' style="color:red">FLAG: 64-characters-of-random-alphanumerics</h2>
        elif tag[0] == 'h2':
            if len(tag[1]) > 0:
                flag = parser.data[0]
                flags.append(flag[6:])
for flag in flags:
    print(flag)