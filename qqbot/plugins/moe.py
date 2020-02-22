from nonebot import on_command, CommandSession
from bs4 import BeautifulSoup
import aiohttp

moe_url = 'https://zh.moegirl.org/'

# 随便从萌娘百科瞎搞点中文描述
@on_command('moe', aliases=("烧酒"))
async def moe(session: CommandSession):
    name = session.get("name", prompt="没能找到你想要的名字")
    girl_report = await get_girl_informaton(name)
    if girl_report != "":
        await session.send(girl_report)

@moe.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    words = text.split(' ')
    if len(words) < 1:
        session.state["name"] = "no"
    else:
        session.state["name"] = words[0]

async def get_girl_informaton(name):
    url = moe_url + name
    html = await get_body(url)
    if html == None:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    infos = soup.find_all('p')
    msg = url + "\n"
    for p in infos:
        t = p.get_text() 
        t = t.replace(' ', '').replace('\n', '').replace('\t', '')
        if hasChinese(t):
            msg = msg + '\n' + t
        elif len(t) > 0:
            break
    # 字数太多发不出去
    if len(msg) > 3400:
        msg = msg[0:3400] + "..."
    return msg

async def get_body(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                return await response.read()
            return None

# 是否中文开头
def hasChinese(str):
    if len(str) < 1:
        return False
    # 萌娘百科有一行以这个开头的含有中文
    if str.find("window.RLQ") != -1:
        return False
    for ch in str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
