import pip._vendor.requests as requests
import json
import traceback


def wikilookup(server, info):
    title = info.content[7:]
    try:
        r=requests.get("https://minecraft-zh.gamepedia.com/api.php?\
            action=query&prop=info&inprop=url&redirects&format=json&titles="+title)
        if r.status_code==200:
            r.encoding = r.apparent_encoding
            jsObj=json.loads(r.text)
            tmp=jsObj["query"]["pages"]
            pageNumber=str(tmp)[2:]
            num=0
            for i in pageNumber:
                if i=="-":
                    num=num+1
                else:
                    try:
                        k=int(i)
                    except:
                        break
                    else:
                        num=num+1
            pageNumber=pageNumber[:num]
            print(pageNumber)
            print()
            tmp=tmp[pageNumber]
            if pageNumber=="-1":
                server.reply(info,"§4发生错误：§r未找到"+title)
                return
            else:
                link=tmp["fullurl"]
                realtitle=tmp["title"]
                server.execute("tellraw "+info.player+" [{\"text\":\""+realtitle+"\",\"color\":\"gold\",\"bold\":true},{\"text\":\"-\",\"color\":\"reset\"},{\"text\":\""+link+"\",\"color\":\"blue\",\"underlined\":true,\"bold\":true,\"clickEvent\":{\"action\":\"open_url\",\"value\":\""
                    +link+"\"}}]")
                return

        else:
            server.reply(info,"§4发生错误：§rGamepedia的服务器又丝滑了")
            return
    except:
        exceptinfo=traceback.format_exc()
        server.reply(info,"§4发生错误：§r"+exceptinfo)

def on_user_info(server, info):
    if info.content.startswith("!!wiki "):
        wikilookup(server, info)

    
