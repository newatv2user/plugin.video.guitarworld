import xbmcplugin
import xbmcgui, xbmc
from xbmcgui import ListItem
import xbmcaddon
import sys
import urllib, urllib2
import re
import brightcovePlayer
import CommonFunctions
import os, cookielib
import StorageServer
import hosts

addon = xbmcaddon.Addon()
AddonId = addon.getAddonInfo('id')

# For parsedom
common = CommonFunctions
common.dbg = False
common.dbglevel = 3
# initialise cache object to speed up plugin operation
cache = StorageServer.StorageServer(AddonId)

thisPlugin = int(sys.argv[1])

baseLink = "http://www.guitarworld.com"

rootDir = addon.getAddonInfo('path')
next_thumb = os.path.join(rootDir, 'next.png')

##################
## Class for items
##################
class MediaItem:
    def __init__(self):
        self.ListItem = ListItem()
        self.Image = ''
        self.Url = ''
        self.Isfolder = False

## Get URL
def getURL(url):
    print 'getURL :: url = ' + url
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
    response = opener.open(url)
    html = response.read()
    ret = {}
    ret['html'] = html 
    return ret

def mainPage():
    showVideosSection(baseLink+'/features/videos')
    
def showVideosSection(link):
    #print 'showVideosSection'
    link = urllib.unquote(link)

    data = cache.cacheFunction(getURL, link)
    if not data:
        return
    page = data['html']
    #page = load_page(link)
    
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    videos = common.parseDOM(page, "div", {"class": "node_article"})
    MediaItems = []
    for video in videos:
        #print video
        title_smaller = common.parseDOM(video, "h1", {"class": "title_smaller"})
        if not title_smaller:
            continue
        title_smaller = title_smaller[0]
        videoTitle = common.parseDOM(title_smaller, "a", ret="title")
        if not videoTitle:
            continue
        videoTitle = videoTitle[0]
        videoTitle = common.replaceHTMLCodes(videoTitle)
        
        videoLink = common.parseDOM(title_smaller, "a", ret="href")[0]
        
        PlotLine1 = common.parseDOM(video, "span", {"class": "posted_date"})
        if not PlotLine1:
            PlotLine1 = ''
        else:
            PlotLine1 = PlotLine1[0]
        
        featured_node_image = common.parseDOM(video, "div", {"class": "featured-node-image"})
        if not featured_node_image:
            videoImg = ''
        else:
            featured_node_image = featured_node_image[0]
            videoImg = common.parseDOM(featured_node_image, "img", ret="src")[0]
            
        PlotDesc = common.parseDOM(video, "p")
        if not PlotDesc:
            PlotDesc = ''
        else:
            PlotDesc = PlotDesc[0]
            PlotDesc = common.stripTags(PlotDesc)
        Plot = PlotLine1 + '\n' + PlotDesc
        
        Mediaitem = MediaItem()
        Mediaitem.Image = videoImg
        paramS = {"action":"playVideo","link":baseLink+videoLink}
        Mediaitem.Url = sys.argv[0] + "?" + urllib.urlencode(paramS)
        Mediaitem.ListItem.setInfo('video', { 'Title': videoTitle, 'Plot': Plot})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(videoTitle)
        Mediaitem.ListItem.setProperty('IsPlayable', 'true')
        MediaItems.append(Mediaitem)
        
        #addDirectoryItem(videoTitle, {"action":"playVideo","link":baseLink+videoLink}, videoImg, False)
    
    # Next Page
    pagination = common.parseDOM(page, "ul", {"class": "pager"})
    if pagination:
        pagination = pagination[0]
        pager_next_last = common.parseDOM(pagination, "li", {"class": "pager-next last"})
        if pager_next_last:
            pager_next_last = pager_next_last[0]
            Next = common.parseDOM(pager_next_last, "a", ret="href")
            if Next:
                Next = Next[0]
                Mediaitem = MediaItem()
                Title = "Next"
                Mediaitem.Image = next_thumb
                paramS = {"action":"showVideosSection","link":baseLink+Next}
                Mediaitem.Url = sys.argv[0] + "?" + urllib.urlencode(paramS)
                Mediaitem.ListItem.setInfo('video', { 'Title': Title})
                Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
                Mediaitem.ListItem.setLabel(Title)
                Mediaitem.Isfolder = True
                MediaItems.append(Mediaitem)
                #addDirectoryItem('Next', {"action":"showVideosSection","link":baseLink+Next})
                
    # Current Issue Bonus Videos
    links_secondary_menu = common.parseDOM(page, "ul", {"class": "links secondary-menu"})
    if links_secondary_menu:
        links_secondary_menu = links_secondary_menu[0]
        lis = common.parseDOM(links_secondary_menu, "li")
        for li in lis:
            Title = common.stripTags(li)
            if not 'Videos' in Title:
                continue
            Href = common.parseDOM(li, "a", ret="href")[0]
            Mediaitem = MediaItem()
            paramS = {"action":"showBonusVideosSection","link":Href}
            Mediaitem.Url = sys.argv[0] + "?" + urllib.urlencode(paramS)
            Mediaitem.ListItem.setInfo('video', { 'Title': Title})
            Mediaitem.ListItem.setLabel(Title)
            Mediaitem.Isfolder = True
            MediaItems.append(Mediaitem)
            
    # Jump to Page
    Mediaitem = MediaItem()
    Title = "Jump to Page"
    paramS = {"action":"jumpToPage"}
    Mediaitem.Url = sys.argv[0] + "?" + urllib.urlencode(paramS)
    Mediaitem.ListItem.setInfo('video', { 'Title': Title})
    Mediaitem.ListItem.setLabel(Title)
    Mediaitem.Isfolder = True
    MediaItems.append(Mediaitem)
    
    addDir(MediaItems)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    ## Set Default View Mode. This might break with different skins. But who cares?
    SetViewMode()
    
def showBonusVideosSection(link):
    #print 'showBonusVideosSection'
    link = urllib.unquote(link)

    data = cache.cacheFunction(getURL, link)
    if not data:
        return
    page = data['html']
    
    contentDiv = common.parseDOM(page, "div", {"style": "width:300px;float:right;padding-bottom:10px;"})
    if not contentDiv:
        return
    contentDiv = contentDiv[0]
    links = re.compile('href="(.+?)">(.+?)<').findall(contentDiv)
    MediaItems = []
    for Url, Title in links:
        if 'store.guitarworld.com' in Url:
            continue
        Title = common.replaceHTMLCodes(Title)
        Mediaitem = MediaItem()
        paramS = {"action":"playVideo","link":Url}
        Mediaitem.Url = sys.argv[0] + "?" + urllib.urlencode(paramS)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title})
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.ListItem.setProperty('IsPlayable', 'true')
        MediaItems.append(Mediaitem)
    
    addDir(MediaItems)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def jumpToPage():
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(0, 'Jump to Page #')
    if d:
        showVideosSection(baseLink+'/features/videos?page='+d)

def playVideo(link):
    #print 'playVideo'
    ulink = urllib.unquote(link)
    data = cache.cacheFunction(getURL, ulink)
    if not data:
        xbmcplugin.setResolvedUrl(thisPlugin, False, xbmcgui.ListItem())
        return
    page = data['html']
    #page = load_page(ulink)
    contentIds = common.parseDOM(page, "param", {"name": "@videoPlayer"}, ret="value")
    if not contentIds:
        #xbmcplugin.setResolvedUrl(thisPlugin, False, xbmcgui.ListItem())
        node_article = common.parseDOM(page, "div", {"class": "node_article"})[0]
        videolinks = hosts.resolve(node_article)
        if videolinks:
            videolink = videolinks[0]
            xbmcplugin.setResolvedUrl(thisPlugin, True, xbmcgui.ListItem(path=videolink))
        return
    #videoPlayer = re.compile("brightcove_mediaId: ([0-9]*),").search(page).group(1)
    
    #splits = ulink.rsplit('/', 1)
    #contentId = int(splits[1])
    stacked_url = 'stack://'
    for contentId in contentIds:
        contentId = int(contentId)
        stream = brightcovePlayer.play(contentId, ulink)
    
        rtmpbase = stream[1][0:stream[1].find("&")]
        finalurl = None
        if not 'edgefcs.net' in rtmpbase:
            playpath = stream[1][stream[1].find("&") + 1:]
            finalurl = rtmpbase + ' playpath=' + playpath
        else:
            postfix = stream[1][stream[1].find("?") :]
            postfix2 = "&videoId=" + str(contentId) + "&lineUpId=&pubId=616302933001&playerId=798983031001&affiliateId="
            app = "ondemand" + postfix + postfix2
        
            swfUrl = "http://admin.brightcove.com/viewer/us20120711.1450/federatedVideoUI/BrightcovePlayer.swf?uid=42300475817"
        
            pageUrl = ulink
        
            playpath = stream[1][stream[1].find("&") + 1:] + postfix2
            finalurl = rtmpbase + " app=" + app + " swfUrl=" + swfUrl + " pageUrl=" + pageUrl + " playpath=" + playpath
            
        if finalurl:
            stacked_url += finalurl.replace(',',',,')+' , '
    
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(stream[0], path=stacked_url)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    
# Set View Mode selected in the setting
def SetViewMode():
    try:
        # if (xbmc.getSkinDir() == "skin.confluence"):
        if addon.getSetting('view_mode') == "1": # List
            xbmc.executebuiltin('Container.SetViewMode(502)')
        if addon.getSetting('view_mode') == "2": # Big List
            xbmc.executebuiltin('Container.SetViewMode(51)')
        if addon.getSetting('view_mode') == "3": # Thumbnails
            xbmc.executebuiltin('Container.SetViewMode(500)')
        if addon.getSetting('view_mode') == "4": # Poster Wrap
            xbmc.executebuiltin('Container.SetViewMode(501)')
        if addon.getSetting('view_mode') == "5": # Fanart
            xbmc.executebuiltin('Container.SetViewMode(508)')
        if addon.getSetting('view_mode') == "6":  # Media info
            xbmc.executebuiltin('Container.SetViewMode(504)')
        if addon.getSetting('view_mode') == "7": # Media info 2
            xbmc.executebuiltin('Container.SetViewMode(503)')
            
        if addon.getSetting('view_mode') == "0": # Media info for Quartz?
            xbmc.executebuiltin('Container.SetViewMode(52)')
    except:
        print "SetViewMode Failed: " + addon.getSetting('view_mode')
        print "Skin: " + xbmc.getSkinDir()

def addDir(Listitems):
    if Listitems is None:
        return
    Items = []
    for Listitem in Listitems:
        Item = Listitem.Url, Listitem.ListItem, Listitem.Isfolder
        Items.append(Item)
    print thisPlugin
    handle = thisPlugin
    xbmcplugin.addDirectoryItems(handle, Items)
   
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    
    return param
    
if not sys.argv[2]:
    mainPage()
else:
    params = get_params()
    if params['action'] == "showVideosSection":
        showVideosSection(params['link'])
    elif params['action'] == "showBonusVideosSection":
        showBonusVideosSection(params['link'])
    elif params['action'] == "jumpToPage":
        jumpToPage()
    elif params['action'] == "playVideo":
        playVideo(params['link'])
    else:
        mainPage()
