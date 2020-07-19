# WikiRequests
这是一个MCDR插件，可以在游戏中通过查询命令`!!wiki <标题>`来查询[中文Minecraft Wiki](https://minecraft-zh.gamepedia.com)上的页面。
若查询到页面，将会返回页面名称和链接。若无此页面，则会回复未找到此页面。若HTTP请求失败，则会回复Gamepedia的服务器又丝滑了。
若查询时出现异常，异常将会被捕获并将Traceback回复给玩家。

感谢[OasisAkari](https://github.com/OasisAkari)和他的QQ机器人提供了创作灵感。
感谢[佛冷](https://github.com/Fallen-Breath)的MCDR。~~MCDR是天下第一的服务端守护进程不接受反驳~~
