import httplib
from pyamf import AMF0, AMF3

from pyamf import remoting, register_class
from pyamf.remoting.client import RemotingService

#playerKey = "AQ~~,AAAA0Zd2KCE~,a1ZzPs5ODGffVvk2dn1CRCof3Ru_I9gE"
playerKey = "AQ~~,AAAAj36EdAk~,0qwz1H1Ey92wZ6vLZcchClKTXdFbuP3P"

height = 1080
const = "cc04dc97246830b634b140979bdbd193aca2d468"
#const = "044379f4d0f21be4792958b06c1023d13d6774ce"
#playerID = 1379595107001
playerID = 798983031001
#publisherID = 90719631001
publisherID =  616302933001

class ContentOverride(object):
    #def __init__(self, contentId, contentType = 1, target = 'videoList'):
    def __init__(self, contentId=0, contentType=0, target='videoPlayer'):
        self.contentType = contentType
        self.contentId = contentId
        self.target = target
        self.contentIds = None
        self.contentRefId = None
        self.contentRefIds = None
        #self.contentType = 1
        #self.contentType = 0
        self.featureId = float(0)
        self.featuredRefId = None
        
class ViewerExperienceRequest(object):
    def __init__(self, URL, contentOverrides, experienceId, playerKey, TTLToken=''):
        self.TTLToken = TTLToken
        self.URL = URL
        self.deliveryType = float(0)
        self.contentOverrides = contentOverrides
        #self.contentOverrides = []
        self.experienceId = experienceId
        self.playerKey = playerKey

def build_amf_request(const, playerID, videoPlayer, publisherID):
    env = remoting.Envelope(amfVersion=3)
    env.bodies.append(
        (
            "/1",
            remoting.Request(
                target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById",
                body=[const, playerID, videoPlayer, publisherID],
                envelope=env
            )
        )
    )
    return env

def build_amf_request2(const, contentID, url):
    register_class(ContentOverride, 'com.brightcove.experience.ContentOverride')    
    content_override = ContentOverride(contentID)
    register_class(ViewerExperienceRequest, 'com.brightcove.experience.ViewerExperienceRequest')
    viewer_exp_req = ViewerExperienceRequest(url, [content_override], playerID, playerKey)
    env = remoting.Envelope(amfVersion=3)
    env.bodies.append(
                      ("/1",
                       remoting.Request(target="com.brightcove.experience.ExperienceRuntimeFacade.getDataForExperience",
                                        body=[const, viewer_exp_req], envelope=env)
                       )
                      )
    return env

def get_clip_info(const, playerID, videoPlayer, publisherID, link):
    conn = httplib.HTTPConnection("c.brightcove.com")
    #envelope = build_amf_request(const, playerID, videoPlayer, publisherID)
    envelope = build_amf_request2(const, videoPlayer, link)
    conn.request("POST", "/services/messagebroker/amf?playerKey=" + playerKey, str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    return response  

'''def play(videoPlayer):
    rtmpdata = get_clip_info(const, playerID, videoPlayer, publisherID)
    print rtmpdata
    streamName = ""
    streamUrl = rtmpdata['FLVFullLengthURL'];
    
    for item in sorted(rtmpdata['renditions'], key=lambda item:item['frameHeight'], reverse=False):
        streamHeight = item['frameHeight']
        
        if streamHeight <= height:
            streamUrl = item['defaultURL']
    
    streamName = streamName + rtmpdata['displayName']
    return [streamName, streamUrl];'''

def play(videoPlayer, link):
    rtmpdata = get_clip_info(const, playerID, videoPlayer, publisherID, link)
    #print rtmpdata
    streamName = ""
    streamUrl = rtmpdata['programmedContent']['videoPlayer']['mediaDTO']['FLVFullLengthURL']
    
    for item in sorted(rtmpdata['programmedContent']['videoPlayer']['mediaDTO']['renditions'], 
                       key=lambda item:item['frameHeight'], reverse=False):
        streamHeight = item['frameHeight']
        
        if streamHeight <= height:
            streamUrl = item['defaultURL']
    
    streamName = streamName + rtmpdata['programmedContent']['videoPlayer']['mediaDTO']['displayName']
    return [streamName, streamUrl];
