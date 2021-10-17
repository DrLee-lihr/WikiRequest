import json
import re
import traceback
import requests
from mcdreforged.api.all import *

server_interface: ServerInterface
interwiki_list = {}


def reply(source: CommandSource, text: RTextList, is_regex: bool = False, server: ServerInterface = None):
    if is_regex:
        server.say(text)
    else:
        source.reply(text)


@new_thread
def interwiki_add(source: CommandSource, context: dict):
    print(str(context))
    link = context["link"]
    index = context["index"]
    r = requests.get(context["link"] + "api.php?action=query&meta=siteinfo&format=json")
    try:
        r_json = json.loads(r.content)
        site_name = r_json["query"]["general"]["mainpage"]
    except:
        reply(source, RTextList(
            RText("发生错误：", RColor.red),
            RText("该链接并非指向一个有效的MediaWiki站点。（链接格式：https://???.???.???/??/）", RColor.white)
        ))
        return
    interwiki_list[index] = link
    reply(source, RTextList(
        RText("成功添加了interwiki：", RColor.aqua),
        RText(site_name, RColor.dark_aqua)
    ))


def interwiki_listing(source: CommandSource, context: dict):
    reply(source, RTextList("已添加了如下interwiki:\n", str(interwiki_list)))


@new_thread
def interwiki_del(source: CommandSource, context: dict):
    try:
        index = context["index"]
        link = interwiki_list.pop(index)
        r = requests.get(link + "api.php?action=query&meta=siteinfo&format=json")
        reply(source, RTextList(
            RText("成功删除了interwiki：", RColor.aqua),
            RText(json.loads(r.content)["query"]["general"]["mainpage"], RColor.dark_aqua)
        ))
    except:
        except_info = traceback.format_exc()
        reply(source, RTextList(
            RText("发生错误：", RColor.red),
            RText(except_info, RColor.white)
        ))


def wiki_help(source: CommandSource, context: dict):
    reply(source, RTextList(
        RText("!!wiki lookup <pagename>", RColor.gray), RText("在Wiki上查询页面。", RColor.white), "\n",
        RText("!!wiki interwiki add <index> <link>", RColor.gray), RText("添加interwiki。", RColor.white), "\n",
        RText("!!wiki interwiki list", RColor.gray), RText("列出所有已添加的interwiki。", RColor.white), "\n",
        RText("!!wiki interwiki del <index>", RColor.gray), RText("删除interwiki。", RColor.white), "\n",
        RText("!!wiki help", RColor.gray), RText("显示此条帮助。", RColor.white), "\n",
        RText("!!iw <...>", RColor.gray), RText("等价于!!wiki interwiki", RColor.white), "\n",
        RText("[[pagename]]", RColor.gray), RText("快速在Wiki上查询页面。", RColor.white)
    ))


@new_thread
def lookup(source: CommandSource, name: dict, is_regex=False, server: ServerInterface = None):
    global server_interface
    name = name["page_name"]
    site_link = "https://minecraft.fandom.com/zh/"
    for index in list(interwiki_list.keys()):
        if name.startswith(index):
            site_link = interwiki_list[index]
            name = name[len(index) + 1:]
            break
    link = f"{site_link}api.php?action=query&prop=info|extracts&inprop=url&redirects" \
           f"&exsentences=1&format=json&titles={name}"
    try:
        print(f"requesting {link} for {name}")
        r = requests.get(link)
        print(f"request finished,status:{str(r.status_code)}")
        print(r.text)
        if r.status_code == 200:
            r.encoding = r.apparent_encoding
            result: dict = json.loads(r.text)
            page_info: dict = result["query"]["pages"]
            if "-1" in page_info:
                page_id = list(page_info.keys())[0]
                link = page_info[page_id]["fullurl"]
                real_title = page_info[page_id]["title"]
                try:
                    extract = page_info[page_id]["extract"]
                    extract = re.sub(r"<.*?>", "", extract)
                    extract = re.sub("\n", "", extract)
                except KeyError:
                    reply(source, RTextList(RText("(no TextExtracts)")), is_regex, server)
                    extract = ""
                reply(source, RTextList(RText("您要的", RColor.gray),
                                        RText(name, RColor.dark_gray)), is_regex, server)
                if real_title != name:
                    reply(source, RTextList(RText(f"(重定向到{real_title})", RColor.white)), is_regex, server)
                reply(source, RTextList(
                    RText("：", RColor.gray), "\n",
                    RText(link, RColor.blue).c(action=RAction.open_url, value=link), "\n",
                    RText(extract, RColor.white)
                ), is_regex, server)
            else:
                reply(source, RTextList(RText(f"找不到条目:{name}。", RColor.red)), is_regex, server)
        else:
            reply(source, RTextList(
                RText("发生错误：", RColor.red),
                RText(f"请求出错。请求状态码:{r.status_code}", RColor.white)
            ), is_regex, server)
    except:
        reply(source, RTextList(
            RText("发生错误：", RColor.red),
            RText(traceback.format_exc(), RColor.white)
        ), is_regex, server)


request_node = Literal("lookup").then(
    GreedyText("page_name").runs(lookup)
)

interwiki_node = Literal("interwiki").then(
    Literal("add").then(Text("index").then(
        GreedyText("link").runs(interwiki_add)))).then(
    Literal("list").runs(interwiki_listing)).then(
    Literal("del").then(Text("index").runs(interwiki_del)))

help_node = Literal("help").runs(wiki_help)

iw_redirect = Literal("!!iw").redirects(interwiki_node)

command = Literal("!!wiki").then(request_node).then(interwiki_node).then(help_node)


def on_load(server: PluginServerInterface, info: Info):
    global interwiki_list, server_interface
    server_interface = server.as_basic_server_interface()
    server.register_command(command)
    server.register_command(iw_redirect)
    server.register_help_message("!!wiki help", "查询Wiki Request插件的帮助。")
    interwiki_list = \
        server.as_plugin_server_interface().load_config_simple(
            file_name="interwiki.json", default_config={"en": "https://minecraft.fandom.com/"})


def on_user_info(server: PluginServerInterface, info: Info):
    content = info.content
    page_list = re.findall(r"\[\[.*?]]", content)
    for page_name in page_list:
        lookup(info.to_command_source(), {"page_name": page_name[2:-2]}, is_regex=True, server=server)


def on_unload(server: ServerInterface):
    server.as_plugin_server_interface().save_config_simple(config=interwiki_list, file_name="interwiki.json")
