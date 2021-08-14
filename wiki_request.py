import json
import re
import traceback
import requests
from mcdreforged.api.all import *

PLUGIN_METADATA = {
    'id': 'wiki_request',
    'version': '2.0.0',
    'name': 'Wiki Request Plugin',
    'description': 'A plugin to look up the Minecraft Wiki',
    'author': 'DrLee_lihr',
    'link': 'https://github.com/DrLee-lihr/WikiRequest',
    'dependencies': {'mcdreforged': '>=1.0.0'}
}

languages_list = ['zh:', 'en:', 'cs:', 'de:', 'el:', 'es:', 'fr:', 'hu:', 'it:',
                  'ja:', 'ko:', 'nl:', 'pl:', 'pt:', 'ru:', 'th:', 'tr:', 'uk:']


@new_thread
def wiki_request(source: CommandSource, context: dict):
    name: str = context["page_name"]
    link = "https://minecraft.fandom.com/"
    language = 'zh'
    temp2 = True
    for temp1 in languages_list:
        if name.startswith(temp1):
            language = name[:2]
            name = name[3:]
            temp2 = False
    link = link + language + "/api.php?action=query&prop=info|extracts&inprop=url&redirects" + \
           "&exsentences=1&format=json&titles=" + name
    try:
        print("requesting " + link + ' for ' + name)
        r = requests.get(link)
        print("request finished,status:" + str(r.status_code))
        if r.status_code == 200:
            r.encoding = r.apparent_encoding
            result = json.loads(r.text)
            page_info = result["query"]["pages"]
            try:
                temp = page_info["-1"]
            except IndexError:
                page_number = str(page_info)[2:]
                num = 0
                for i in page_number:
                    try:
                        temp = int(i)
                    except:
                        break
                    else:
                        num = num + 1
                page_number = page_number[:num]
                link = page_info[str(page_number)]["fullurl"]
                real_title = page_info[str(page_number)]["title"]
                extract = page_info[str(page_number)]["extract"]
                extract = re.sub(r"<.*?>", "", extract)
                if real_title != name:
                    source.reply(RTextList(
                        RText("您要的", RColor.gray),
                        RText(name, RColor.dark_gray),
                        RText("(重定向到%s)" % real_title, RColor.white),
                        RText("：", RColor.gray),
                        "\n",
                        RText(link, RColor.blue).c(action=RAction.open_url, value=link),
                        "\n",
                        RText(extract, RColor.white)
                    ))
                else:
                    source.reply(RTextList(
                        RText("您要的", RColor.gray),
                        RText(real_title, RColor.dark_gray),
                        RText("：", RColor.gray),
                        "\n",
                        RText(link, RColor.blue).c(action=RAction.open_url, value=link),
                        "\n",
                        RText(extract, RColor.white)
                    ))
            else:
                source.reply(RText("找不到条目。", RColor.red))

        else:
            source.reply(RTextList(
                RText("发生错误：", RColor.red),
                RText("请求出错。", RColor.white)
            ))
    except:
        except_info = traceback.format_exc()
        source.reply(RTextList(
            RText("发生错误：", RColor.red),
            RText(except_info, RColor.white)
        ))


command = Literal("!!wiki").then(
    GreedyText("page_name").runs(wiki_request)
)


def on_load(server: ServerInterface, info: Info):
    server.register_command(command)
    server.register_help_message("!!wiki <pagename>", "查询Minecraft Wiki上的页面。")
