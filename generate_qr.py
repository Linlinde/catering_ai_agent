import qrcode
import os
from dotenv import load_dotenv

# 加载环境变量（如果在服务器上使用，也可以直接指定）
load_dotenv()

# 从环境变量中获取 URL，如未设置则使用默认的 IP（请自行修改为你的访问地址）
url = os.environ.get("APP_URL", "47.121.141.247")
img = qrcode.make(url)
img.save("qrcode.png")
print("二维码生成成功，文件名：qrcode.png")
