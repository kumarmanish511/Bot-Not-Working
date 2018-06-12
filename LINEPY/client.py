# -*- coding: utf-8 -*-
from akad.ttypes import Message
from .api import LineApi
from .models import LineModels
from random import randint

import json, requests, re

def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            args[0].callback.other("You must login to LINE")
    return checkLogin

class LineClient(LineApi, LineModels):

    def __init__(self, id=None, passwd=None, authToken=None, certificate=None, systemName=None, showQr=False, appName=None, phoneName=None, keepLoggedIn=True):
        
        LineApi.__init__(self)

        if not (authToken or id and passwd):
            self.qrLogin(keepLoggedIn=keepLoggedIn, systemName=systemName, appName=appName, showQr=showQr)
        if authToken:
            if appName:
                appOrPhoneName = appName
            elif phoneName:
                appOrPhoneName = phoneName
            self.tokenLogin(authToken=authToken, appOrPhoneName=appName)
        if id and passwd:
            self.login(_id=id, passwd=passwd, certificate=certificate, systemName=systemName, phoneName=phoneName, keepLoggedIn=keepLoggedIn)

        self._messageReq = {}
        self.profile    = self._client.getProfile()
        self.groups     = self._client.getGroupIdsJoined()

        LineModels.__init__(self)

    """User"""

    @loggedIn
    def getProfile(self):
        return self._client.getProfile()

    @loggedIn
    def getSettings(self):
        return self._client.getSettings()

    @loggedIn
    def getUserTicket(self):
        return self._client.getUserTicket()

    @loggedIn
    def updateProfile(self, profileObject):
        return self._client.updateProfile(0, profileObject)

    @loggedIn
    def updateSettings(self, settingObject):
        return self._client.updateSettings(0, settingObject)

    @loggedIn
    def updateProfileAttribute(self, attrId, value):
        return self._client.updateProfileAttribute(0, attrId, value)

    """Operation"""

    @loggedIn
    def fetchOperation(self, revision, count):
        return self._client.fetchOperations(revision, count)

    @loggedIn
    def getLastOpRevision(self):
        return self._client.getLastOpRevision()

    """Message"""

    @loggedIn
    def sendMessage(self, to, text, contentMetadata={}, contentType=0):
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        try: message = self._client.sendMessage(self._messageReq[to], msg)
        except Exception as e: print(e)
        return message
    
    """ Usage:
        @to Integer
        @text String
        @dataMid List of user Mid
    """
    @loggedIn
    def sendText(self, Tomid, text):
        msg = Message()
        msg.to = Tomid
        msg.text = text

        return self._client.sendMessage(0, msg)

    @loggedIn
    def sendMessage1(self, messageObject):
        return self._client.sendMessage(0,messageObject)

    @loggedIn
    def sendMessageWithMention(self, to, text='', dataMid=[]):
        arr = []
        list_text=''
        if '[list]' in text:
            i=0
            for l in dataMid:
                list_text+='\n@[list-'+str(i)+']'
                i=i+1
            text=text.replace('[list]', list_text)
        elif '[list-' in text:
            text=text
        else:
            i=0
            for l in dataMid:
                list_text+=' @[list-'+str(i)+']'
                i=i+1
            text=text+list_text
        i=0
        for l in dataMid:
            mid=l
            name='@[list-'+str(i)+']'
            ln_text=text.replace('\n',' ')
            if ln_text.find(name):
                line_s=int(ln_text.index(name))
                line_e=(int(line_s)+int(len(name)))
            arrData={'S': str(line_s), 'E': str(line_e), 'M': mid}
            arr.append(arrData)
            i=i+1
        contentMetadata={'MENTION':str('{"MENTIONEES":' + json.dumps(arr).replace(' ','') + '}')}
        return self.sendMessage(to, text, contentMetadata)
    @loggedIn
    def mention(self, to, nama):
        aa = ""
        bb = ""
        strt = int(0)
        akh = int(0)
        nm = nama
        myid = self.talk.getProfile().mid
        if myid in nm:    
            nm.remove(myid)
        for mm in nm:
          akh = akh + 6
          aa += """{"S":"""+json.dumps(str(strt))+""","E":"""+json.dumps(str(akh))+""","M":"""+json.dumps(mm)+"},"""
          strt = strt + 7
          akh = akh + 1
          bb += "@nrik \n"
        aa = (aa[:int(len(aa)-1)])
        text = bb
        try:
            msg = Message()
            msg.to = to
            msg.text = text
            msg.contentMetadata = {'MENTION':'{"MENTIONEES":['+aa+']}'}
            msg.contentType = 0
            self.talk.sendMessage(0, msg)
        except Exception as error:
           print(error, 'def Mention')
    @loggedIn
    def sendSticker(self, to, packageId, stickerId):
        contentMetadata = {
            'STKVER': '100',
            'STKPKGID': packageId,
            'STKID': stickerId
        }
        return self.sendMessage(to, '', contentMetadata, 7)
        
    @loggedIn
    def sendContact(self, to, mid):
        contentMetadata = {'mid': mid}
        return self.sendMessage(to, '', contentMetadata, 13)

    @loggedIn
    def sendGift(self, productId, productType):
        if productType not in ['theme','sticker']:
            raise Exception('Invalid productType value')
        contentMetadata = {
            'MSGTPL': str(randint(0, 12)),
            'PRDTYPE': productType.upper(),
            'STKPKGID' if productType == 'sticker' else 'PRDID': productId
        }
        return self.sendMessage(to, '', contentMetadata, 9)

    @loggedIn
    def removeMessage(self, messageId):
        return self._client.removeMessage(messageId)
        
    @loggedIn
    def removeAllMessages(self, lastMessageId):
        return self._client.removeAllMessages(0, lastMessageId)
        
    @loggedIn
    def sendChatChecked(self, consumer, messageId):
        return self._client.sendChatChecked(0, consumer, messageId)

    @loggedIn
    def sendEvent(self, messageObject):
        return self._client.sendEvent(0, messageObject)

    @loggedIn
    def getLastReadMessageIds(self, chatId):
        return self._client.getLastReadMessageIds(0,chatId)

    """Contact"""
        
    @loggedIn
    def blockContact(self, mid):
        return self._client.blockContact(0, mid)

    @loggedIn
    def unblockContact(self, mid):
        return self._client.unblockContact(0, mid)

    @loggedIn
    def findAndAddContactsByMid(self, mid):
        return self._client.findAndAddContactsByMid(0, mid)

    @loggedIn
    def findAndAddContactsByUserid(self, userid):
        return self._client.findAndAddContactsByUserid(0, userid)

    @loggedIn
    def findContactsByUserid(self, userid):
        return self._client.findContactByUserid(userid)

    @loggedIn
    def findContactByTicket(self, ticketId):
        return self._client.findContactByUserTicket(ticketId)

    @loggedIn
    def getAllContactIds(self):
        return self._client.getAllContactIds()

    @loggedIn
    def getBlockedContactIds(self):
        return self._client.getBlockedContactIds()

    @loggedIn
    def getContact(self, mid):
        return self._client.getContact(mid)

    @loggedIn
    def getContacts(self, midlist):
        return self._client.getContacts(midlist)

    @loggedIn
    def getFavoriteMids(self):
        return self._client.getFavoriteMids()

    @loggedIn
    def getHiddenContactMids(self):
        return self._client.getHiddenContactMids()

    @loggedIn
    def reissueUserTicket(self, expirationTime=100, maxUseCount=100):
        return self._client.reissueUserTicket(expirationTime, maxUseCount)
    
    @loggedIn
    def cloneContactProfile(self, mid):
        contact = self.getContact(mid)
        profile = self.profile
        profile.displayName = contact.displayName
        profile.statusMessage = contact.statusMessage
        profile.pictureStatus = contact.pictureStatus
        self.updateProfileAttribute(8, profile.pictureStatus)
        return self.updateProfile(profile)

    """Group"""
    
    @loggedIn
    def findGroupByTicket(self, ticketId):
        return self._client.findGroupByTicket(ticketId)

    @loggedIn
    def acceptGroupInvitation(self, groupId):
        return self._client.acceptGroupInvitation(0, groupId)

    @loggedIn
    def acceptGroupInvitationByTicket(self, groupId, ticketId):
        return self._client.acceptGroupInvitationByTicket(0, groupId, ticketId)

    @loggedIn
    def cancelGroupInvitation(self, groupId, contactIds):
        return self._client.cancelGroupInvitation(0, groupId, contactIds)

    @loggedIn
    def createGroup(self, name, midlist):
        return self._client.createGroup(0, name, midlist)

    @loggedIn
    def getGroup(self, groupId):
        return self._client.getGroup(groupId)

    @loggedIn
    def getGroups(self, groupIds):
        return self._client.getGroups(groupIds)

    @loggedIn
    def getGroupIdsInvited(self):
        return self._client.getGroupIdsInvited()

    @loggedIn
    def getGroupIdsJoined(self):
        return self._client.getGroupIdsJoined()

    @loggedIn
    def inviteIntoGroup(self, groupId, midlist):
        return self._client.inviteIntoGroup(0, groupId, midlist)

    @loggedIn
    def kickoutFromGroup(self, groupId, midlist):
        return self._client.kickoutFromGroup(0, groupId, midlist)

    @loggedIn
    def leaveGroup(self, groupId):
        return self._client.leaveGroup(0, groupId)

    @loggedIn
    def rejectGroupInvitation(self, groupId):
        return self._client.rejectGroupInvitation(0, groupId)

    @loggedIn
    def reissueGroupTicket(self, groupId):
        return self._client.reissueGroupTicket(groupId)

    @loggedIn
    def updateGroup(self, groupObject):
        return self._client.updateGroup(0, groupObject)

    """Room"""

    @loggedIn
    def createRoom(self, midlist):
        return self._client.createRoom(0, midlist)

    @loggedIn
    def getRoom(self, roomId):
        return self._client.getRoom(roomId)

    @loggedIn
    def inviteIntoRoom(self, roomId, midlist):
        return self._client.inviteIntoRoom(0, roomId, midlist)

    @loggedIn
    def leaveRoom(self, roomId):
        return self._client.leaveRoom(0, roomId)

    """Call"""
        
    @loggedIn
    def acquireCallRoute(self, to):
        return self._client.acquireCallRoute(to)

    """Manga"""
    def getMangaSource(self):
        get = requests.get(self.server.MANGA_READER_API_HOST)
        sources = get.json()
        mangaSource = []
        for source in sources:
            ID = str(source["id"])
            name = source["name"]
            language = source["lang_name"]
            src = {
                'ID':ID,
                'name':name,
                'language':language
            }
            mangaSource.append(src)
        return mangaSource

    def getMangaRank(self, sourceID):
        get = requests.get(self.server.MANGA_READER_API_HOST+sourceID)
        mangas = get.json()
        mangaList = []
        for manga in mangas:
            ID = str(manga["id"])
            rank = str(manga["rank"])
            name = manga["name"]
            mangaList.append(name+"(#"+rank+") ID: "+ID)
        mangaList.sort(key=self.naturalKeys)
        return mangaList

    def getMangaRankMatched(self, sourceID, name):
        mangaLists = [x.lower() for x in self.getMangaRank(sourceID)]
        matching = [s for s in mangaLists if name in s]
        return matching

    def getMangaDetailed(self, sourceID, mangaID):
        get = requests.get(self.server.MANGA_READER_API_HOST+sourceID+"/"+mangaID)
        detail = get.json()
        rank = str(detail["rank"])
        categories = str(detail["categories"])
        name = detail["name"]
        author = detail["author"]
        description = detail["des"]
        totalChapters = str(len(detail["chapters"]))
        image = detail["image"]
        output = "Rank: "+rank+"\nName: "+name+"\nAuthor: "+author+"\nTotal Chapters: "+totalChapters+"\n\nDescription:\n"+description
        return {'details':output, 'thumb':image, 'chapters':detail["chapters"]}

    def getMangaImage(self, sourceID, mangaID, chapterID):
        get = requests.get(self.server.MANGA_READER_API_HOST+sourceID+"/"+mangaID+"?cid="+chapterID)
        chapters = get.json()
        return chapters

    """Others"""
    def textCheck(self, text):
        return int(text) if text.isdigit() else text

    def naturalKeys(self, text):
        return [ self.textCheck(c) for c in re.split('(\d+)', text) ]

    def sendMessageV2(self, message):
        return self._client.sendMessage(0, message)