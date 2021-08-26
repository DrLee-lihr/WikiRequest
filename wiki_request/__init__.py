import json
import re
import traceback
import requests
from mcdreforged.api.all import *

PLUGIN_METADATA = {
    'id': 'wiki_request',
    'version': '3.0',
    'name': 'Wiki Request Plugin',
    'description': 'A plugin to look up the Minecraft Wiki',
    'author': 'DrLee_lihr',
    'link': 'https://github.com/DrLee-lihr/WikiRequest',
    'dependencies': {'mcdreforged': '>=2.0.0'}
}

interwiki_list = {}


@new_thread
def interwiki_add(source: CommandSource, context: dict):
    link: str = context["link"] + "api.php?action=query&meta=siteinfo&format=json"
    r = requests.get(link)
    try:
        r_json = json.loads(r.content)
        site_name = r_json["query"]["general"]["mainpage"]
    except:
        source.reply(RTextList(
            RText("发生错误：", RColor.red),
            RText("该链接并非指向一个有效的MediaWiki站点。（链接格式：https://???.???.???/??/）", RColor.white)
        ))
    else:
        interwiki_list[context["index"]] = context["link"]
        source.reply(RTextList(
            RText("成功添加了interwiki：", RColor.aqua),
            RText(site_name, RColor.dark_aqua)
        ))


def interwiki_listing(source: CommandSource, context: dict):
    source.reply("已添加了如下interwiki:\n" + str(interwiki_list))


@new_thread
def interwiki_del(source: CommandSource, context: dict):
    try:
        index = context["index"]
        link = interwiki_list.pop(index)
        r = requests.get(link + "api.php?action=query&meta=siteinfo&format=json")
        source.reply(RTextList(
            RText("成功删除了interwiki：", RColor.aqua),
            RText(json.loads(r.content)["query"]["general"]["mainpage"], RColor.dark_aqua)
        ))
    except:
        except_info = traceback.format_exc()
        source.reply(RTextList(
            RText("发生错误：", RColor.red),
            RText(except_info, RColor.white)
        ))


@new_thread
def wiki_request(source: CommandSource, context: dict):
    name: str = context["page_name"]
    lookup(source, name)


def wiki_help(source: CommandSource, context: dict):
    source.reply(RTextList(
        RText("!!wiki lookup <pagename>", RColor.gray), RText("在Wiki上查询页面。\n", RColor.white),
        RText("!!wiki interwiki add <index> <link>", RColor.gray), RText("添加interwiki。\n", RColor.white),
        RText("!!wiki interwiki list", RColor.gray), RText("列出所有已添加的interwiki。\n", RColor.white),
        RText("!!wiki interwiki del <index>", RColor.gray), RText("删除interwiki。\n", RColor.white),
        RText("!!wiki help", RColor.gray), RText("显示此条帮助。\n", RColor.white),
        RText("!!iw <...>", RColor.gray), RText("等价于!!wiki interwiki", RColor.white),
        RText("[[]]", RColor.gray), RText("快速在Wiki上查询页面。\n", RColor.white)
    ))


def lookup(source: CommandSource, name: str, is_regex=False, server=None):
    site_link = "https://minecraft.fandom.com/zh/"
    for index in list(interwiki_list.keys()):
        if name.startswith(index):
            site_link = interwiki_list[index]
            name = name[len(index) + 1:]
    link = site_link \
           + "api.php?action=query&prop=info|extracts&inprop=url&redirects" + \
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
                    except TypeError:
                        break
                    else:
                        num = num + 1
                page_number = page_number[:num]
                link = page_info[str(page_number)]["fullurl"]
                real_title = page_info[str(page_number)]["title"]
                extract = page_info[str(page_number)]["extract"]
                extract = re.sub(r"<.*?>", "", extract)
                if real_title != name:
                    if is_regex:
                        server.say(RTextList(
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
                            RText(name, RColor.dark_gray),
                            RText("(重定向到%s)" % real_title, RColor.white),
                            RText("：", RColor.gray),
                            "\n",
                            RText(link, RColor.blue).c(action=RAction.open_url, value=link),
                            "\n",
                            RText(extract, RColor.white)
                        ))
                else:
                    if is_regex:
                        server.say(RTextList(
                            RText("您要的", RColor.gray),
                            RText(real_title, RColor.dark_gray),
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
                if is_regex:
                    server.say(RText(f"找不到条目:{name}。", RColor.red))
                else:
                    source.reply(RText(f"找不到条目:{name}。", RColor.red))
        else:
            if is_regex:
                server.say(RTextList(
                    RText("发生错误：", RColor.red),
                    RText("请求出错。", RColor.white)
                ))
            else:
                source.reply(RTextList(
                    RText("发生错误：", RColor.red),
                    RText("请求出错。", RColor.white)
                ))
    except:
        except_info = traceback.format_exc()
        if is_regex:
            server.say(RTextList(
                RText("发生错误：", RColor.red),
                RText(except_info, RColor.white)
            ))
        else:
            source.reply(RTextList(
                RText("发生错误：", RColor.red),
                RText(except_info, RColor.white)
            ))


request_node = Literal("lookup").then(
    GreedyText("page_name").runs(wiki_request)
)

interwiki_node = Literal("interwiki").then(
    Literal("add").then(Text("index").then(GreedyText("link").runs(interwiki_add))).then(
        Literal("list").runs(interwiki_listing).then(
            Literal("del").then(
                Text("index").runs(interwiki_del)
            )
        )
    )
)

help_node = Literal("help").runs(wiki_help)

redirect = Literal("!!iw").redirects(interwiki_node)

command = Literal("!!wiki").then(request_node).then(interwiki_node).then(help_node)


def on_load(server: PluginServerInterface, info: Info):
    server.register_command(command)
    server.register_command(redirect)
    server.register_help_message("!!wiki help", "查询wiki_request插件的帮助。")


def on_user_info(server: PluginServerInterface, info: Info):
    content = info.content
    page_list = re.findall(r"\[\[.*?\]\]", content)
    for page_name in page_list:
        lookup(info.to_command_source(), page_name, is_regex=True, server=server)
