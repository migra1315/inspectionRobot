import os
import base64
import json
from openai import OpenAI
from speechSynthesizer import SpeechSynthesizerHandler,speechSynthesizerCallback

# 动态设置日志文件路径 - 跨平台兼容
from pathlib import Path
log_dir = Path(__file__).parent
log_file = log_dir / 'nss_ssl_sfagent.log'
os.environ["SSLKEYLOGFILE"] = str(log_file)

class ErrorMonitor():
    def __init__(self):
        self.speechSynthesizer= SpeechSynthesizerHandler()
        self.client = OpenAI(
            # api_key="sk-3kaeuj4oP58oODxlW6Fv0QQYA51220V9BBglUCcSfgk0rvUS",
            # base_url="https://api.moonshot.cn/v1",
            api_key="sk-9c0fea83ac074bcbab481a077d74c83b",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            
        )
    
    # 创建字典作为JSON对象
        example_json_data_1 = {
            "设备名称": "保藏中心22号低温冰箱",
            "设定温度":"-80℃",
            "当前温度": "-80℃",
            "系统状态":"正常，处于合理区间",
            'wellWork': True,
            "response":"保藏中心22号低温冰箱的当前温度是-80摄氏度，位于合理区间，工作状态正常。"
        }
        example_json_string_1 = json.dumps(example_json_data_1, ensure_ascii=False, indent=4)
        
        example_json_data_2 = {
            "设备名称": "保藏中心8号液氮罐",
            "安全余量":"40L",
            "当前余量": "30L",
            "系统状态":"异常，处于不合理区间",
            'wellWork': False,
            "response":"保藏中心8号液氮罐的当前余量是30升，位于不合理区间，请及时处置。"

        }
        example_json_string_2 = json.dumps(example_json_data_2, ensure_ascii=False, indent=4)

        example_json_data_3 = {
            "设备名称": "保藏中心11号低温冰箱",
            '设定温度': '-80℃', 
            '当前温度': '-75℃', 
            '系统状态': '异常，处于不合理区间', 
            'wellWork': False,
            'response': '保藏中心11号低温冰箱的当前温度是-75摄氏度，位于不合理区间，请及时处置。'
        }
        example_json_string_3 = json.dumps(example_json_data_3, ensure_ascii=False, indent=4)

        example_json_data_4 = {
            "设备名称": "保藏中心12号低温冰箱",
            '设定温度': '-80℃', 
            '当前温度': '-80.2℃', 
            '系统状态': '正常，处于合理区间', 
            'wellWork': False,
            'response': '保藏中心12号低温冰箱的当前温度是-80.2摄氏度，位于合理区间，工作状态正常。'
        }
        example_json_string_4 = json.dumps(example_json_data_4, ensure_ascii=False, indent=4)

        self.system_promotion = f""" 
        【任务指令】
        你用来识别生物资源保藏中心的低温冰箱和液氮罐设备面板显示内容，判断设备是否正常工作。
        低温冰箱的实际温度与设定温度差异不能超过2摄氏度，
        液氮罐的当前余量不能低于安全余量。
        根据上传的图像，以json形式输出设备名、合理值、当前值、系统状态、wellWork和response。
        输出值要求可以直接用json解析
        
        【判断逻辑示例】
        - 设定温度：-80℃，当前温度：-78.2℃ → 差值 = 1.8℃ → 正常
        - 设定温度：-80℃，当前温度：-82.5℃ → 差值 = 2.5℃ → 异常，处于不合理区间
        - 设定温度：-80℃，当前温度：-80.2℃ → 差值 = 0.2℃ → 正常
        - 设定温度：-80℃，当前温度：-75℃ → 差值 = 5℃ → 异常，处于不合理区间
        - 安全余量：60L，当前余量：40L → 当前余量40L低于安全余量60L → 异常，处于不合理区间
        - 安全余量：60L，当前余量：70L → 当前余量70L高于安全余量60L → 正常


        【回复要求】
        上传图片作为相机拍摄的面板内容，先判断设备是否正常工作。
        - 温度单位保留“℃”，余量单位保留“L”。
        - 系统状态字段必须为“正常,原因...”或“异常，原因...”。
        - 系统状态正常,wellWork设置为True；系统状态不正常,wellWork设置为False;
        - response描述当前设备状态，是否处于合理区间，如果设备未正常工作，提示用户进行处置。
        - 以 json 格式回复：
        示例 {example_json_string_1}
        示例 {example_json_string_2}
        示例 {example_json_string_3}
        示例 {example_json_string_4}
        """
        
        self.messages =[
                {
                    "role": "system", 
                    "content": self.system_promotion
                }
            ]
    
    def extract_content(self, json_data, object = "response"):
        try:
            content = ""
            data = json.loads(json_data)
            for i in range(len(data[object])):
                content = content + data[object][i]
            return content
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error extracting content: {e}")
            return None
        
    def encode_image(self, image_path):
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # 我们使用标准库 base64.b64encode 函数将图片编码成 base64 格式的 image_url
        image_url = f"data:image/{Path(image_path).suffix};base64,{base64.b64encode(image_data).decode('utf-8')}"
        return image_url
    
    def forward_image(self, image_path, content= ""):
        image_url = self.encode_image(image_path)
        messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url", # <-- 使用 image_url 类型来上传图片，内容为使用 base64 编码过的图片内容
                            "image_url": {
                                "url": image_url,
                            },
                        },
                        {
                            "type": "text",
                            "text":content, # <-- 使用 text 类型来提供文字指令，例如“描述图片内容”
                        },
                    ],
                }
            ]
    
        messages = self.messages.append(messages[0])

        completion = self.client.chat.completions.create(
            model="qwen-vl-plus",
            # model="moonshot-v1-8k-vision-preview",
            messages=self.messages,
            presence_penalty = 1.5,
            response_format = {"type": "json_object"}
        )
        self.messages =[
                {
                    "role": "system", 
                    "content": self.system_promotion
                }
            ]
        chatBot_response = completion.choices[0].message.content
        return chatBot_response
    
    def analyze_image(self, image_path, device_id=None):
        """分析图片 - 兼容性方法"""
        try:
            # 使用现有的forward_image方法
            result = self.forward_image(image_path, "分析这个设备的状态")
            
            # response = self.extract_content(result,"response")
            # # print(response)
            # self.speechSynthesizer.forward(response)
            # self.speechSynthesizer.readSpeech()

            # 尝试解析JSON结果
            if result:
                try:
                    import json
                    return json.loads(result)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，返回默认格式
                    return {
                        "设备名称": f"设备{device_id}" if device_id else "未知设备",
                        "系统状态": "正常",
                        "分析结果": result
                    }
            else:
                return {
                    "设备名称": f"设备{device_id}" if device_id else "未知设备",
                    "系统状态": "分析失败",
                    "分析结果": "无法获取分析结果"
                }
        except Exception as e:
            print(f"AI分析异常: {e}")
            return {
                "设备名称": f"设备{device_id}" if device_id else "未知设备",
                "系统状态": "分析异常",
                "错误信息": str(e)
            }
        
    def forward(self,path):
        chatBot_response = self.forward_image(image_path= path,content="反馈这个设备状态")
        
        data = json.loads(chatBot_response)
        print(data)
        response = self.extract_content(chatBot_response,"response")
        # print(response)
        self.speechSynthesizer.forward(response)
        self.speechSynthesizer.readSpeech()
    

if __name__ == '__main__':
    chatBot = ErrorMonitor()

    for i in range(2,7):
        # 跨平台兼容路径
        current_dir = Path(__file__).parent
        image_path = current_dir / "source" / f"{i}.png"
        print(f"处理图片: {image_path}")
        chatBot_response = chatBot.forward_image(
            image_path=str(image_path),
            content="反馈这个设备状态")
        data = json.loads(chatBot_response)
        print(data)

