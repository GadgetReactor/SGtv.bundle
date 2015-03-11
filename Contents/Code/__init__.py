# -*- coding: utf-8 -*-
# last updated 2014-09-06
# coded by Sean S (GadgetReactor)
# visit www.gadgetreactor.com/portfolio/sgtv for updates 

NAME = 'SG!tv'

ART = 'art-default.jpg'
ICON = 'icon-default.png'
VIDEO_ICON = 'icon-169.png'
ICON_NEXT = 'icon-next.png'
ICON_SEARCH = 'icon-search.png'

import urllib2, re

def openUrl(url):
	retries = 0
	while retries < 2:
		try:
			req = urllib2.Request(url, None, {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'})
			content = urllib2.urlopen(req)
			if content.info().getheader('Content-Encoding') == 'gzip':
				buf = StringIO( content.read())
				f = gzip.GzipFile(fileobj=buf)
				data = f.read()
			else:
				data=content.read()
			content.close()
			data = str(data).replace('\n','')
			return data
			
		except urllib2.HTTPError,e:
			retries += 1
			print ' - Retries: ' + str(retries) + str(e.code)
			continue
		else:
			break
	else:
		print 'Fetch of ' + url + ' failed after ' + str(retries) + 'tries.'

###################################################################################################
def Start():

  Plugin.AddPrefixHandler('/video/SG!tv', MainMenu, NAME, ICON, ART)

  ObjectContainer.title1 = NAME
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(VIDEO_ICON)
  VideoClipObject.art = R(ART)

###################################################################################################
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key = Callback(Episodes, title = 'Recently Released', channel='new', show='all'), title = 'Recently Released'))
	oc.add(DirectoryObject(key = Callback(Shows, channel='channel5'), title = 'Channel 5', thumb=R('channel5.jpg')))
	oc.add(DirectoryObject(key = Callback(Shows, channel='channel8'), title = 'Channel 8', thumb=R('channel8.jpg')))
	oc.add(DirectoryObject(key = Callback(Shows, channel='channelu'), title = 'Channel U', thumb=R('channelu.jpg')))
	oc.add(DirectoryObject(key = Callback(Shows, channel='okto'), title = 'Okto', thumb=R('okto.png')))
	oc.add(DirectoryObject(key = Callback(Shows, channel='suria'), title = 'Suria', thumb=R('suria.png')))
	oc.add(DirectoryObject(key = Callback(Shows, channel='vasantham'), title = 'Vasantham', thumb=R('vasantham.png')))
	oc.add(DirectoryObject(key = Callback(Youtube, user='channelnewsasia'), title = 'Channel News Asia', thumb=R('cna.png')))
	oc.add(DirectoryObject(key = Callback(Youtube, user='wahbanana'), title = 'WahBanana', thumb=R('wahbanana.jpg')))
	oc.add(DirectoryObject(key = Callback(Viddsee, page='0', type = 'popular'), title = 'Viddsee', thumb=R('viddsee.png')))
	
	return oc

###################################################################################################

def htmlParse(str):
	str=str.replace('\\x3a', ':')
	str=str.replace('\\x2f', '/')	
	str=re.sub('&amp;','&',str)
	str=re.sub('&#39;',"'",str)
	str=str.replace('&quot;', '"')
	str=str.replace('&#187;', '-')
	str=str.replace('&#160;', ':')
	str=re.sub(r'<.*?>','', str)
	return str

###################################################################################################		
		
def Shows(channel):
	oc = ObjectContainer()
	data = openUrl("http://xin.msn.com/en-sg/video/catchup/")
	showlist  = re.compile('<div data-tabkey="tab-(\d+)".*?homepage\|%s\|tab\|(.*?)\|.+?:&quot;(.+?)&quot' % (channel)).findall(data)

	for tab, show, thumb in showlist:
		image = 'http:'+ thumb.replace('&amp;','&')
		oc.add(DirectoryObject(key = Callback(Episodes, show=show, channel=channel, tab=tab), title = show))	

	return oc

###################################################################################################	

def Youtube(user):
	oc = ObjectContainer()
	youtube_url = "http://gdata.youtube.com/feeds/api/users/" + user + "/uploads?v=2&alt=json"

	data = JSON.ObjectFromURL (youtube_url)
		
	for entry in data["feed"]["entry"]:
		title = entry["title"]["$t"]
		video_id = entry["media$group"]["yt$videoid"]["$t"]
		desc = entry["media$group"]["media$description"]["$t"]
		image = "http://img.youtube.com/vi/" + video_id + "/0.jpg"
		video = VideoClipObject(
								title = title,
								summary = desc,
								#originally_available_at = video_date,
								#rating = video_rating,
								url = "http://youtube.com/watch?v="+video_id
								)
		
		oc.add(video)
	return oc
			
###################################################################################################	

def Viddsee(page, type):
	oc = ObjectContainer()
	
#	type examples: | popular | genre/drama | genre/comedy |  
	viddsee_url = "https://www.viddsee.com/v1/browse/"+type+"?current_page="+page+"&per_page=12"
	data = JSON.ObjectFromURL(viddsee_url)

	for video in data["videos"]:
		video_url = video["embed_url"]
		video_url.replace ("http\://player\.vimeo\.com/video", "http://vimeo\.com")
		Log (video_url)
		print video_url
		video = VideoClipObject(
								title = video["title"], 
								#summary = htmlParse(video["description_long"]),
								#tagline = video["description_short"],
								#genres = video["genres"],
								#duration = video["duration"],
								#rating = float (video["rating"]["rating_like"]),
								#year = video["year"],
								#thumb = video["thumbnail_url"],
								#art = video["photo_large_url"],
								url =  video_url
								)	
		oc.add(video)
		
	page = str(int(page)+1)
	oc.add(DirectoryObject(key = Callback(Viddsee, page=page, type = 'popular'), title = 'Viddsee', thumb=R('viddsee.png')))
	return oc
	
###################################################################################################	
def Episodes(show, channel, tab):
	oc = ObjectContainer()

	data=openUrl("http://xin.msn.com/en-sg/video/catchup/")

	if "new" in channel:
		episodelist = re.compile('<li.+?href="(.+?)".+?:&quot;(.+?)&quot.+?<h4>(.+?)</h4>.+?"duration">(.+?)<.+?</li>').findall(data)	

	else:
		episodechunk  = re.compile('class="section tabsection horizontal".+?data-section-id="%s".+?<div data-tabkey="%s"(.+?)</ul>' % (channel, tab)).search(data).group(1)
		episodelist = re.compile('<li.+?href="(.+?)".+?:&quot;(.+?)&quot.+?<h4>(.+?)</h4>.+?"duration">(.+?)<.+?</li>').findall(episodechunk)	

	for episode_url, thumb, title, time in episodelist:
		episode_url = "http://xin.msn.com" + episode_url
		title=htmlParse(title)									
		
		image = 'http:'+ thumb.replace('&amp;','&')
		infoLabels={'Title': title, 'Duration':time}
		#oc.add(DirectoryObject(key = Callback(playBack, title = title, url = episode_url), title = title))
		#oc.add(CreateObject(url=Callback(playBack2, url=episode_url), media_type="video", title=title))
		thumbUrl = "http://img1.catalog.video.msn.com/Image.aspx?uuid=" + thumb + "&w=400&h=300"
		#mo = MediaObject(parts=[PartObject(key=HTTPLiveStreamURL(Callback(GetVideo, url=episode_url, channel=channel)))])
		#rating_key = episode_url
		#vco = VideoClipObject(key=title, rating_key=rating_key, title=title)
		video = VideoClipObject(
								title = title,
								#summary = video_summary,
								#originally_available_at = video_date,
								#rating = video_rating,
								url = episode_url
								)
		
		oc.add(video)
		
	return oc
