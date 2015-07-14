# -*- coding: utf-8 -*-
# last updated 2015-07-14
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

	oc.add(DirectoryObject(key = Callback(Toggle, channel='catchup-listing'), title = 'Recently Released'))
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

def Thumb(url):
	try:
		data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))


###################################################################################################

def Toggle(channel):
	oc = ObjectContainer()
	data=openUrl("http://video.toggle.sg/en/%s" % channel)
	showlist  = re.compile('<div class="tg-teaser-item".*?data-srcset="(.+?)".+?href="(.+?)">(.+?)<').findall(data)

	for image, url, show in showlist:
		if "http" not in image:
			image = "http://video.toggle.sg" + image
		video = VideoClipObject(
								title = show,
								#originally_available_at = video_date,
								#rating = video_rating,
								thumb = Callback(Thumb, url=image),
								url = url,
								)

		oc.add(video)
	return oc


###################################################################################################

def Shows(channel):
	oc = ObjectContainer()
	data=openUrl("http://tv.toggle.sg/en/%s/shows" % channel)
	showlist  = re.compile('data-src.+?"(.+?)".+?href="(.+?)">(.+?)<').findall(data)

	"""
	Channel 8
	id: 5275960,
    navigationId: 5013778,
    channelId: 331027,

	Channel 5
	id: 5275964,
	navigationId: 5013778,
	channelId: 331025,
	"""

	for image, url, show in showlist:
		if "http" not in image:
			image = "http://video.toggle.sg" + image
		oc.add(DirectoryObject(key = Callback(Episodes, show=show, channel=channel, tab=url, page=0), title = show, thumb = Callback(Thumb, url=image)))

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

								url = "http://youtube.com/watch?v="+video_id,
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
								thumb = Callback(Thumb, url=video["thumbnail_url"]),
								#art = video["photo_large_url"],
								url =  video_url,
								)
		oc.add(video)

	page = str(int(page)+1)
	oc.add(DirectoryObject(key = Callback(Viddsee, page=page, type = 'popular'), title = 'Viddsee', thumb=R('viddsee.png')))
	return oc

###################################################################################################
def Episodes(show, channel, tab, page):
	oc = ObjectContainer()

	data=openUrl(tab + "/episodes")
	meta = re.compile('10, 0,  (.+?), (.+?), (.+?)\);',re.DOTALL).search(data)

	data = openUrl ("http://tv.toggle.sg/en/blueprint/servlet/toggle/paginate?pageSize=10&pageIndex="+str(page)+"&contentId="+meta.group(1)+"&navigationId="+meta.group(2)+"&"+meta.group(3)+"=1")

	episodechunk  = re.compile('<li>(.*?)<\/li>').findall(data)

	for chunk in episodechunk:
		episodelist = re.compile('img src="(.+?)".+?.+?item__tags(.+?)<\/div>.+?href="(.+?)">(.+?)<\/a>.+?<p>(.+?)<\/p>').search(chunk)
		vip_status = episodelist.group(2)
		if "vip" not in vip_status:
			episode_url = episodelist.group(3)
			title = str(episodelist.group(4))
			desc = episodelist.group(5)
			image = episodelist.group(1)

			video = VideoClipObject(
							title = title,
							#summary = video_summary,
							#originally_available_at = video_date,
							#rating = video_rating,
							thumb = Callback(Thumb, url=image),
							url = episode_url,
							)

			oc.add(video)

	pagination = re.compile ('pagination\'\),(.+?), (.+?), paginateLabel').search(data)
	current_page = int( pagination.group (1) )
	max_page = int ( pagination.group (2) )
	if current_page < max_page:
		page = str(current_page + 1)
		oc.add(DirectoryObject(key = Callback(Episodes, show=show, channel=channel, tab=tab, page=page), title = 'Next Page', ))
	return oc
