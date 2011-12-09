import re
from datetime import datetime

from ircbot.models import Define, Quote
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.template import Template, Context
from django.db.models import Q
from django.core import exceptions
from yardbird.irc import IRCResponse
from yardbird.shortcuts import render_to_response, render_to_reply
from yardbird.shortcuts import render_silence, render_error, render_quick_reply
from yardbird.utils.decorators import require_addressing, require_chanop
import Weather
import urllib
import simplejson
import dictclient
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup


more_results = []

def test(request):
    print "test"
    return render_silence()

# definitions
    
def learn(request,tag,definition):
    try:
        last_define = Define.objects.filter(tag__iexact=tag).order_by('index')[0]
        index = last_define.index +1
    except:
        index = 1
    Define.objects.create(tag=tag,text=definition,index=index,created_by=request.nick)
    return IRCResponse(request.reply_recipient, "%s[%i] learned." % (tag,index))
        
def show_definition(request,tag, index=0):
    index = int(index)

    global more_results
    del more_results[:]
    try:
        # if index specified try to get the item at the index
        if index > 0:
            define = Define.objects.get(tag__iexact=tag,index=index)
            define_text = "%s[%i]: %s" % (tag,index,define.text)
            more_results.append(define_text)
        else:
            defines = Define.objects.filter(tag__iexact=tag).order_by('id')
            count = 1
            if len(defines)== 0:
                return IRCResponse(request.reply_recipient, "%s is not defined." % (tag))
            for define in defines:
                define_text = "%s[%i]: %s" % (tag,define.index,define.text)
                more_results.append(define_text)
                count += 1
        more_results.reverse()
        result = more_results.pop()
        return IRCResponse(request.reply_recipient, result)
    except:
        return IRCResponse(request.reply_recipient, "%s[%i] is not defined." % (tag,index))
        
def who_set(request,tag,index=0):
    index = int(index)
    print "looking up %s [%i]" % (tag,index)
    try:
        if index > 0:
            define = Define.objects.get(tag__iexact=tag,index=index)
        else:
            define = Define.objects.filter(tag__iexact=tag).order_by('id')[0]
            index = 1
            
 
        return IRCResponse(request.reply_recipient, "%s[%i] is set by %s on %s." %
                           (tag,define.index,define.created_by,define.created.strftime("%A, %d. %B %Y %I:%M%p")))
    except:
        return IRCResponse(request.reply_recipient, "%s[%i] is not defined." % (tag,index))
        
def forget(request,tag,index=0):
    index = int(index)
    print "forgetting %s " % tag
    try:
        if index > 0:
            define = Define.objects.get(tag__iexact=tag,index=index)
        else:
            define = Define.objects.filter(tag__iexact=tag).order_by('id')[0]
            index = 1
        define.delete()
        return IRCResponse(request.reply_recipient, "%s[%i] forgotten." % (tag,index))
    except:
        return IRCResponse(request.reply_recipient, "%s[%i] is not defined." % (tag,index))
        
def search (request,search_str,nick=None):
    q = Q(tag__icontains=search_str) | Q (text__icontains = search_str)
    global more_results
    del more_results[:]
    try:
        if nick is not None:
            defines = Define.objects.filter(q,created_by=nick).order_by('id')
        else:
            defines = Define.objects.filter(q).order_by('id')
    except:
        return IRCResponse(request.reply_recipient, "No results found.")
        
    count = 0
    search_tags = "Tags: "
    for define in defines:
        count += 1
        define_text = "[%i/%i] %s[%i]: %s" % (count,len(defines),define.tag,define.index,define.text)
        if count > 1:
            search_tags += ", %s[%i]" % (define.tag, define.index)
        else:
            search_tags += "%s[%i]" % (define.tag, define.index)
        more_results.append(define_text)
        
    more_results.reverse()
    if count < 2:
        result = more_results.pop()
        return IRCResponse(request.reply_recipient, result) 
    else:
        return IRCResponse(request.reply_recipient, search_tags) 
       
        
# quotes
def add_quote(request,quote):
    try:
        last_quote = Quote.objects.all().order_by('index')[0]
        index = last_define.index +1
    except:
        index = 1
    Quote.objects.create(text=quote,index=index,created_by=request.nick)
    return IRCResponse(request.reply_recipient, "Quote %i added." % index)   

def get_quote(request,quote_id=0):
    quote_id = int(quote_id)
    try:
        if quote_id > 0 :
            quote = Quote.objects.get(index=quote_id)
        else:
            quote = Quote.objects.order_by("?")[0]
        return IRCResponse(request.reply_recipient, "[%i] %s"% (quote.index,quote.text) )  
    except:
        return IRCResponse(request.reply_recipient, "Quote not found." )  

def del_quote(request,quote_id):
    quote_id = int(quote_id)
    try:
        quote = Quote.objects.get(index=quote_id)
        quote.delete()
        return IRCResponse(request.reply_recipient, "Quote %i deleted." % quote_id )
    except:
        return IRCResponse(request.reply_recipient, "Quote not found." )
# misc

def track(request,tracking_number):
    tracking_number = parse_terms(tracking_number)
    if re.match(r'(?i)1Z\w+?$',tracking_number):
        url = "http://wwwapps.ups.com/WebTracking/processInputRequest?sort_by=status&tracknums_displayed=1&TypeOfInquiryNumber=T&loc=en_US&InquiryNumber1=%s" %tracking_number
    elif count_digits(tracking_number) == 12 or count_digits(tracking_number) == 15:
        url = "http://www.fedex.com/Tracking?tracknumbers=%s" % tracking_number
    #elif re.match(r'8.+?',tracking_number):
    #    url = "http://track.dhl-usa.com/TrackByNbr.asp?ShipmentNumber=%s" % tracking_number
    #elif re.match(r'(?i)70.+?|03.+?|23.+?|EA.+?|RA.+?|CP.+?',tracking_number):
    elif count_digits(tracking_number) == 22:
        url = "http://trkcnfrm1.smi.usps.com/PTSInternetWeb/InterLabelInquiry.do?origTrackNum=%s" % tracking_number
    else:
        return IRCResponse(request.reply_recipient, "Unknown tracking number format." )
     
    tinyurl = tiny_url(url)
    return IRCResponse(request.reply_recipient, "Tracking url: %s" % tinyurl )       

# count a number of digits in a given string
def count_digits(input_string):
    count = 0
    for letter in input_string:
        if re.match('\d',letter) : count += 1
        
    return count

def dict(request,word):
    global more_results
    del more_results[:]
    try:
        my_dict = dictclient.Connection('dict.org')
        result =my_dict.define("wn",word)[0]
        result_str =  ' '.join(result.getdefstr().split('\n'))
        result_list = re.split(r'(\d+:\D+)', result_str)
        for i in range(0,len(result_list)):
            if (i+1) % 2 == 0:
                #definition = "%s defintion %i of %i: %s " % (word,(i+1)/2,len(result_list)/2,result_list[i])
                more_results.append(result_list[i])
        
        more_results.reverse()
        result = more_results.pop()
            
        return IRCResponse(request.reply_recipient, "%s" % result)
    except:
        return IRCResponse(request.reply_recipient, "Could not lookup %s" % word)

def get_weather(request,location):
    print "getting weather at %s " % location
    global more_results
    del more_results[:]
    
    try:
        station = Weather.location2station(location)
        weather = Weather.Station(station[0])
        weather.update(live=True)
        
        more_string = "Dew point: %s, Pressure: %s, Humidity: %i%%, Wind: %s " % (
            weather.data['dewpoint_string'],weather.data['pressure_string'],weather.data['relative_humidity'],weather.data['wind_string'])
        
        more_results.append(more_string)
        
        return IRCResponse(request.reply_recipient, "Weather at %s: %s %s %s " %
                           (weather.data['city'],weather.data['weather'],weather.data['temperature_string'],weather.data['observation_time']))
        
    except:
        return IRCResponse(request.reply_recipient, "Weather at %s is not found." % location)

def magic(request, query):

    print "magicing for %s " % query
    global more_results
    del more_results[:]

    query = urllib.urlencode({'q' : query })
    url = "http://magiccards.info/query?%s" % query
    search_results = urllib.urlopen(url)
    
    soup = BeautifulSoup(search_results.read())
    cards = soup.findAll("table")

    for card in cards[3:]:
        try:
            title = card.contents[1].contents[3].contents[1].contents[1].contents[0]
            cost = card.contents[1].contents[3].contents[3].contents[0]
            text = ' '.join(card.contents[1].contents[3].contents[5].contents[0].findAll(text=True))
            sets = card.contents[1].contents[5].contents[1].contents[13].contents[0]
            search_result = "%s - %s: %s - %s (%s)" % (title,cost,text,sets,tiny_url(url))
            search_result = search_result.replace('\n','').strip()
            more_results.append(search_result)
        except:
            next
    more_results.reverse()
    try:
   	result = more_results.pop()
    except:
	result = "Card not found"

    return IRCResponse(request.reply_recipient, "%s" % result )

def google(request,query):
    print "googling for %s " % query
    global more_results
    del more_results[:]

    query = urllib.urlencode({'q' : query })
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s'  % query
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    try:
        
        results = json['responseData']['results']
        
        for result in results:
            url = result['url']
            title = clean_html(result['title'])
            content = clean_html(result['content'])
            search_result = "%s - %s: %s" % (url,title,content)
            
            more_results.append(search_result)

        more_results.reverse()    
        result = more_results.pop()
        return IRCResponse(request.reply_recipient, "%s" % result )  
    except:
        return IRCResponse(request.reply_recipient, "No results were found.")

def map(request,location):
    query = parse_terms(location)
    query = urllib.urlencode({'q' : query })
    url = 'http://maps.google.com/?%s'  % query
    tinyurl = tiny_url(url)
    return IRCResponse(request.reply_recipient, "%s" % tinyurl )

def tiny_url(url):
    quoted = urllib.quote_plus(url)
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urllib.urlopen(apiurl + quoted).read()

    return tinyurl

def clean_html(html):
    result = ''.join(BeautifulSoup(html).findAll(text=True))
    result = result.encode('ascii','ignore')
    result = ' '.join(result.split())
    result =  BeautifulStoneSoup(result, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    return result

def more(request):
    global more_results
    if len(more_results)> 0:
        result = more_results.pop()
        return IRCResponse(request.reply_recipient, "%s" % (result) )
    else:
        return IRCResponse(request.reply_recipient, "There is no more.")
        
# try to get terms out of the string
def parse_terms(term_string):
    split_string = re.split(r'\{(.+?)\}',term_string)
    result_string = ""
    if len(split_string) > 1:
        for i in range(0,len(split_string)):
            if (i+1) % 2 == 0:
                # check if its a single word
                if re.match(r'^(\w+?)$',split_string[i]):
                    # try to evaluate it
                    try:
                        eval = Define.objects.filter(tag__iexact=split_string[i]).order_by('id')[0]
                        result_string += "%s" % eval.text
                    except:
                        result_string += "{%s}" % split_string[i]
                elif re.match(r'^(\w+?)\s(\d+?)$',split_string[i]):
                    substr = re.match(r'^(\w+?)\s(\d+?)$',split_string[i])
                    try:
                        eval = Define.objects.get(tag__iexact=substr.group(1),index=substr.group(2))
                        result_string += "%s" % eval.text
                    except:
                        result_string += "{%s}" % split_string[i]
            else:
                result_string += "%s" % split_string[i]
    else:
        return term_string
    
    return result_string
