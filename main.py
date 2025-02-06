from flask import Flask, render_template, request, jsonify
import time
from openai import OpenAI

app = Flask(__name__)

# 全局对话历史记录（实际项目中建议每个用户单独管理会话）
conversation_history = []

# 使用阿里云 dashscope 兼容模式调用 qwen-plus 模型
client = OpenAI(
    api_key="", 
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 菜单数据库：包括传统菜品和海鲜菜品，每道菜增加了“等待时间”、“销量”和“点赞”字段
MENU = {
    "宫保鸡丁": {
        "price": 38,
        "description": "经典川菜，微辣香脆",
        "做法": "采用鸡肉丁、花生米、干辣椒和葱姜爆炒，先炸花生米再炒鸡丁。",
        "适合人群": "爱吃辣、追求口感丰富的人群",
        "推荐指数": "★★★★☆",
        "等待时间": "15分钟",
        "销量": 120,
        "点赞": 85
    },
    "鱼香肉丝": {
        "price": 32,
        "description": "酸甜口味，入口回味",
        "做法": "猪肉丝配以泡椒、木耳、青椒和胡萝卜，炒制时加入鱼香汁。",
        "适合人群": "喜欢酸甜口味及偏好清淡菜品的顾客",
        "推荐指数": "★★★☆☆",
        "等待时间": "12分钟",
        "销量": 98,
        "点赞": 75
    },
    "麻婆豆腐": {
        "price": 28,
        "description": "麻辣鲜香，豆腐滑嫩",
        "做法": "采用嫩豆腐搭配牛肉末、豆瓣酱和花椒粉，高温快炒使豆腐充分入味。",
        "适合人群": "喜欢重口味及麻辣风味的人群",
        "推荐指数": "★★★★☆",
        "等待时间": "10分钟",
        "销量": 110,
        "点赞": 90
    },
    "红烧肉": {
        "price": 45,
        "description": "肥而不腻，入口即化",
        "做法": "选用五花肉，焖煮至软糯后用酱油、糖、料酒及香料慢火煮制。",
        "适合人群": "偏爱传统家常菜及喜欢肉食的顾客",
        "推荐指数": "★★★★★",
        "等待时间": "20分钟",
        "销量": 80,
        "点赞": 70
    },
    # 海鲜菜品
    "清蒸鲈鱼": {
        "price": 68,
        "description": "清蒸鲈鱼，鲜美可口",
        "做法": "将鲈鱼清洗干净，加姜丝和葱段，蒸10-12分钟即可。",
        "适合人群": "喜欢清淡健康饮食的人群",
        "推荐指数": "★★★★☆",
        "等待时间": "18分钟",
        "销量": 65,
        "点赞": 60
    },
    "盐焗大虾": {
        "price": 88,
        "description": "盐焗大虾，香气扑鼻",
        "做法": "选用新鲜大虾，配以盐、胡椒和香料焗制至虾壳微焦。",
        "适合人群": "喜爱海鲜风味的食客",
        "推荐指数": "★★★★★",
        "等待时间": "22分钟",
        "销量": 70,
        "点赞": 68
    },
    "蒜蓉蒸扇贝": {
        "price": 98,
        "description": "蒜蓉蒸扇贝，入口鲜香",
        "做法": "扇贝搭配蒜蓉、黄油和料酒，蒸至刚熟。",
        "适合人群": "追求精致海鲜口感的人群",
        "推荐指数": "★★★★★",
        "等待时间": "16分钟",
        "销量": 55,
        "点赞": 50
    },
    "红烧大黄鱼": {
        "price": 78,
        "description": "红烧大黄鱼，酱香浓郁",
        "做法": "大黄鱼切块，加酱油、糖、料酒和姜片，红烧至汤汁浓稠。",
        "适合人群": "喜好重口味海鲜的顾客",
        "推荐指数": "★★★★☆",
        "等待时间": "20分钟",
        "销量": 60,
        "点赞": 55
    },
    "酱爆蛤蜊": {
        "price": 58,
        "description": "酱爆蛤蜊，香辣诱人",
        "做法": "蛤蜊与豆瓣酱、蒜末和辣椒快速翻炒。",
        "适合人群": "喜爱辣味海鲜的食客",
        "推荐指数": "★★★☆☆",
        "等待时间": "12分钟",
        "销量": 50,
        "点赞": 45
    },
    "辣炒花甲": {
        "price": 48,
        "description": "辣炒花甲，鲜香麻辣",
        "做法": "花甲与辣椒、蒜末和豆瓣酱一同翻炒。",
        "适合人群": "喜欢刺激口味的顾客",
        "推荐指数": "★★★☆☆",
        "等待时间": "10分钟",
        "销量": 52,
        "点赞": 40
    },
    "酱香鲍鱼": {
        "price": 128,
        "description": "酱香鲍鱼，味道醇厚",
        "做法": "鲍鱼先炖后炸，再配以特制酱汁调味。",
        "适合人群": "追求高档海鲜体验的食客",
        "推荐指数": "★★★★★",
        "等待时间": "25分钟",
        "销量": 35,
        "点赞": 30
    },
    "清蒸龙利鱼": {
        "price": 66,
        "description": "清蒸龙利鱼，鲜嫩无比",
        "做法": "龙利鱼加姜丝和葱段清蒸，保留原味。",
        "适合人群": "偏爱清淡健康饮食的人群",
        "推荐指数": "★★★★☆",
        "等待时间": "15分钟",
        "销量": 60,
        "点赞": 55
    },
    "香煎带鱼": {
        "price": 55,
        "description": "香煎带鱼，外焦里嫩",
        "做法": "带鱼切段后腌制，再煎至两面金黄。",
        "适合人群": "喜欢煎制海鲜的顾客",
        "推荐指数": "★★★☆☆",
        "等待时间": "14分钟",
        "销量": 58,
        "点赞": 50
    },
    "蒜蓉粉丝蒸虾": {
        "price": 75,
        "description": "蒜蓉粉丝蒸虾，鲜美多汁",
        "做法": "新鲜虾与粉丝、蒜蓉一起蒸制，出锅后淋上热油提香。",
        "适合人群": "喜爱传统海鲜做法的食客",
        "推荐指数": "★★★★☆",
        "等待时间": "17分钟",
        "销量": 62,
        "点赞": 57
    }
}

# 用于限制返回菜品必须严格来自数据库的字符串
db_dishes = ", ".join(MENU.keys())

def ai_detect_menu_query(user_text):
    """
    判断用户输入是否为整体菜单查询：
    - 若询问整体菜单（如“你们有什么菜色？”），返回 True；
    - 若只询问单个菜品信息（如“宫保鸡丁多少钱？”），返回 False。
    """
    prompt = (
        "你是一个智能查询判断助手，请判断下面的用户输入是否是在询问整体菜单信息，而非单个菜品的价格或详情。"
        "如果是整体菜单查询，请输出 '菜单查询'；如果只是询问某道菜品，请输出 '非菜单查询'。"
        "请仅输出这两个选项中的一个。"
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_text},
    ]
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=False
        )
        result = response.choices[0].message.content.strip()
        print("菜单查询检测结果：", result)
        return result == "菜单查询"
    except Exception as e:
        print("ai_detect_menu_query 调用失败：", e)
        return False

def generate_menu_summary():
    """
    根据数据库生成整体菜单摘要回答，要求只引用数据库中的信息。
    """
    menu_data = ""
    for dish, details in MENU.items():
        menu_data += (
            f"{dish}: 价格 {details['price']}元, 做法：{details['做法']}, "
            f"适合人群：{details['适合人群']}, 推荐指数：{details['推荐指数']}, "
            f"等待时间：{details['等待时间']}, 销量：{details['销量']}，点赞：{details['点赞']}\n"
        )
    prompt = (
        "你是川林酒家AI点餐助手，一个专业、友好且细致的餐饮服务助手。"
        "请严格依据以下菜单数据回答用户“你们有什么菜色？”的问题，只能推荐数据库中存在的菜品。"
        "菜单数据如下：\n" + menu_data +
        "请用简洁的语言回答。"
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "你们有什么菜色？"}
    ]
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("生成菜单摘要出错：", e)
        return full_menu_response()

def full_menu_response():
    """
    返回完整菜单展示文本，作为备用方案。
    """
    response_text = "以下是我们的菜单：\n\n"
    responses = []
    for dish, menu_item in MENU.items():
        info = (
            f"【{dish}】\n"
            f"价格：{menu_item['price']}元\n"
            f"做法：{menu_item['做法']}\n"
            f"适合人群：{menu_item['适合人群']}\n"
            f"推荐指数：{menu_item['推荐指数']}\n"
            f"等待时间：{menu_item['等待时间']}\n"
            f"销量：{menu_item['销量']}，点赞：{menu_item['点赞']}"
        )
        responses.append(info)
    response_text += "\n\n".join(responses)
    response_text += "\n\n请问您想点哪一道菜？"
    return response_text

def ai_detect_intent(user_text):
    """
    判断用户输入的意图：
    - 如果为点餐，请返回格式 "点餐: 菜品名称1, 菜品名称2"，且返回的菜品必须来自数据库 (db_dishes)；
    - 如果为咨询，请返回格式 "咨询:"。
    """
    prompt = (
        "你是一个智能意图检测助手，请判断下面用户的输入属于“点餐”还是“咨询”。"
        "如果用户意图为点餐，请返回格式 \"点餐: 菜品名称1, 菜品名称2\"；"
        "如果为咨询，请返回格式 \"咨询:\"。"
        "注意：返回的菜品名称必须严格来自以下数据库： " + db_dishes + " 。"
        "请仅返回以上格式的结果。"
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_text},
    ]
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=False
        )
        result = response.choices[0].message.content.strip()
        if result.startswith("点餐:"):
            dishes_str = result[len("点餐:"):].strip()
            dishes = [dish.strip() for dish in dishes_str.split(",") if dish.strip()] if dishes_str else []
            return {"intent": "点餐", "dishes": dishes}
        elif result.startswith("咨询:"):
            return {"intent": "咨询", "dishes": []}
        else:
            return {"intent": "咨询", "dishes": []}
    except Exception as e:
        print("意图检测出错：", e)
        return {"intent": "咨询", "dishes": []}

def get_chat_response(user_input, max_retries=3):
    """
    调用对话接口生成回复，结合对话历史，要求回答时严格引用数据库中的菜品信息。
    """
    global conversation_history
    system_prompt = (
        "你是川林酒家AI点餐助手，一个专业、友好且细致的餐饮服务助手。"
        "回答问题时请严格只使用以下数据库中的菜品： " + db_dishes + " 。"
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_input})
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(f"调用对话接口失败，重试 {retry_count+1}/{max_retries} 次：{e}")
            retry_count += 1
            time.sleep(1)
    return "调用对话接口多次失败，请您换个问题试试。"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "请输入内容。"})
    
    # 记录用户输入
    conversation_history.append({"role": "user", "content": user_input})
    
    # 如果为订单确认（例如“确认点餐”）
    if "确认" in user_input and "点餐" in user_input:
        answer = "您的订单已提交，请稍候，我们将尽快为您安排出餐。"
        conversation_history.append({"role": "assistant", "content": answer})
        return jsonify({"response": answer})
    
    # 判断是否为整体菜单查询
    if ai_detect_menu_query(user_input):
        answer = generate_menu_summary()
        conversation_history.append({"role": "assistant", "content": answer})
        return jsonify({"response": answer})
    
    # 否则判断用户意图：点餐或咨询
    intent_result = ai_detect_intent(user_input)
    if intent_result["intent"] == "咨询":
        answer = get_chat_response(user_input)
        conversation_history.append({"role": "assistant", "content": answer})
        return jsonify({"response": answer})
    elif intent_result["intent"] == "点餐":
        if intent_result["dishes"]:
            responses = []
            for dish in intent_result["dishes"]:
                if dish in MENU:
                    menu_item = MENU[dish]
                    info = (
                        f"【{dish}】\n"
                        f"价格：{menu_item['price']}元\n"
                        f"做法：{menu_item['做法']}\n"
                        f"适合人群：{menu_item['适合人群']}\n"
                        f"推荐指数：{menu_item['推荐指数']}\n"
                        f"等待时间：{menu_item['等待时间']}\n"
                        f"销量：{menu_item['销量']}，点赞：{menu_item['点赞']}"
                    )
                    responses.append(info)
                else:
                    responses.append(f"抱歉，我们数据库中没有【{dish}】。")
            answer = "检测到您有点餐需求，以下是相关菜品信息：\n\n" + "\n\n".join(responses)
            answer += "\n\n请问是否确认下单？（回复：确认点餐 或 取消）"
            conversation_history.append({"role": "assistant", "content": answer})
            return jsonify({"response": answer})
        else:
            answer = full_menu_response()
            conversation_history.append({"role": "assistant", "content": answer})
            return jsonify({"response": answer})
    else:
        answer = get_chat_response(user_input)
        conversation_history.append({"role": "assistant", "content": answer})
        return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
