import urllib2
import cookielib
from prime.data import uname, password


def sendsms(number, message):
    message = "+".join(message.split(' '))
    url = 'http://site24.way2sms.com/Login1.action?'
    data = 'username=' + uname + '&password=' + password + '&Submit=Sign+in'
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120')]
    usock = opener.open(url, data)
    jession_id = str(cj).split('~')[1].split(' ')[0]
    send_sms_url = 'http://site24.way2sms.com/smstoss.action?ssaction=ss&Token=' + \
        jession_id + '&mobile=' + number + '&message=' + message + '&msgLen=136'
    opener.addheaders = [
        ('Referer', 'http://site24.way2sms.com/sendSMS?Token=' + jession_id)]
    sms_sent_page = opener.open(send_sms_url)
