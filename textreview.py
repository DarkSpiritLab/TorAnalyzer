import requests
import json
with open("token") as f:
    token=f.readline()
if(token==""):
    print("token not exists")
    exit()
class TextReviewer():
    '''
    review text content
    PostContent to review get result format in json.
    '''
    def __init__(self):
        url=r"https://aip.baidubce.com/rest/2.0/antispam/v2/spam?access_token="+token
        Header={"Content-type":"application/x-www-form-urlencoded"}

    def postContent(self,content):
        '''
        :param content:string (text to review)
        :return: json result
        '''
        data={"content":content.encode('utf-8')}
        response=requests.post(url=self.url,data=data,headers=self.Header)
        reJson=response.content.decode("utf-8")
        return reJson

    def paserResultJson(self,reJson):

        j=json.loads(reJson)
        if("errno" not in j):
            # error string
            print("error")
            return
        elif(j["errno"]!="0"):
            #print err no
            print("errno code"+j["errno"])
            pass
        else:
            #normal return
            pass