import requests
import json
import traceback
from mcdreforged.api.all import *

PLUGIN_METADATA = {
    'id': 'wiki_request',
    'version': '2.0.0',
    'name': 'Wiki Request Plugin',
    'description': 'A plugin to look up the Minecraft Wiki',
    'author': 'DrLee_lihr',
    'link': 'https://github.com/DrLee-lihr/WikiRequest'
}

languages_list: list[str] = ['zh:', 'en:', 'cs:', 'de:', 'el:', 'es:', 'fr:', 'hu:', 'it:',
                             'ja:', 'ko:', 'nl:', 'pl:', 'pt:', 'ru:', 'th:', 'tr:', 'uk:']


@new_thread
def wiki_request(source: CommandSource, context: dict):
    name = dict["page_name"]
    link = 'https://minecraft.fandom.com/'
    if name.startswith(languages_list):
        language = name[:1]
        name = name[3:]
    else:
        language = "zh"
    link = link + language + '/api.php'
    try:
        r = requests.get(link, params={'action': 'query', 'format': 'json', 'props': 'info|extracts',
                                       'titles': name, 'redirects': 1, 'exsentences': '1'})
        if r.status_code == 200:
            r.encoding = r.apparent_encoding
            result = json.loads(r.text)
            page_info = result["query"]["pages"]

            try:
                temp = result["query"]["pages"]["-1"]
            except Exception:
                link = page_info[0]["fullurl"]
                real_title = page_info[0]["title"]
                extract = page_info[0]["extract"]
                if real_title != name:
                    return RTextList(
                        RText("您要的", RColor.gray),
                        RText(name, RColor.dark_gray),
                        RText("(重定向到%s)" % real_title, RColor.white),
                        RText("：", RColor.gray),
                        "\n",
                        RText(link, RColor.dark_blue).c(action=RAction.open_url, value=link),
                        "\n",
                        RText(extract, RColor.white)
                    )
                else:
                    return RTextList(
                        RText("您要的", RColor.gray),
                        RText(real_title, RColor.dark_gray),
                        RText("：", RColor.gray),
                        "\n",
                        RText(link, RColor.dark_blue).c(action=RAction.open_url, value=link),
                        "\n",
                        RText(extract, RColor.white)
                    )
            else:
                return RText("找不到条目。", RColor.red),

        else:
            return RTextList(
                RText("发生错误：", RColor.red),
                RText("请求超时。", RColor.white)
            )
    except:
        except_info = traceback.format_exc()
        return RTextList(
            RText("发生错误：", RColor.red),
            RText(except_info, RColor.white)
        )


command = Literal("!!wiki").then(
    GreedyText("page_name").runs(wiki_request)
)


def on_load(server: ServerInterface, info: Info):
    server.register_command(command)
    server.register_help_message("!!wiki <pagename>", "查询Minecraft Wiki上的页面。")


