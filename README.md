# WikiRequest
~~此插件已被弃用，请使用OasisAkari的QQbot的[MCDR移植版本](https://github.com/Teahouse-Studios/_LittleK_)~~ OA的QQbot的MCDR移植已被弃用（2021.8.9），于是我又回来做1.0支持了

**1.0版本已支持，0.x版本不再提供支持，旧插件保留最后版本。**

这是一个MCDR插件，可以在游戏中通过查询命令`!!wiki <标题>`来查询[中文Minecraft Wiki](https://minecraft.fandom.com)上的页面。

若查询到页面，将会返回页面名称和链接。若无此页面，则会回复未找到此页面。若HTTP请求失败，则会回复请求超时。

若查询时出现异常，异常将会被捕获并将Traceback回复给玩家。


注意：该插件依赖requests库，请提前使用`pip install requests`安装该库。

感谢[OasisAkari](https://github.com/OasisAkari)和他的QQ机器人提供了创作灵感。
感谢[佛冷](https://github.com/Fallen-Breath)的MCDR。
