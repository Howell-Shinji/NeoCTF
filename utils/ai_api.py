import json
import requests
import os
import random
from datetime import datetime
from openai import OpenAI

class CTFSecurityAI:
    """CTF平台安全AI接口类，提供自动攻防、场景生成和分析功能"""
    
    def __init__(self):
        # API密钥配置（实际部署时应从环境变量或配置文件获取）
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.qwen_api_key = os.environ.get("QWEN_API_KEY", "")
        
        # 初始化API客户端
        if self.deepseek_api_key:
            self.deepseek_client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
        
        # 设置硅基流动API配置
        if self.qwen_api_key:
            self.qwen_headers = {
                "Authorization": f"Bearer {self.qwen_api_key}",
                "Content-Type": "application/json"
            }
            self.qwen_url = "https://api.siliconflow.cn/v1/chat/completions"
        
        # 本地模型配置
        self.local_url = "http://127.0.0.1:1234/v1/chat/completions"
        
        # 局域网模型配置
        self.lan_url = "http://192.168.1.108:1234/v1/chat/completions"
        
        # 支持的模型列表
        self.supported_models = {
            "local": [
                "qwen/qwen2.5-72b-instruct", 
                "qwen/qwen3-4b", 
                "google/gemma-3-4b", 
                "deepseek/deepseek-r1-0528-qwen3-8b",
                "qwen2.5-vl-instruct",
                "qwen2.5-omni-instruct"
            ],
            "lan": [
                "qwen/qwen2.5-72b-instruct", 
                "qwen/qwen3-4b", 
                "google/gemma-3-4b",
                "deepseek/deepseek-r1-0528-qwen3-8b",
                "qwen2.5-vl-instruct",
                "qwen2.5-omni-instruct"
            ],
        }
        
        # 模型选项映射
        self.model_options = {
            "Deepseek-R1": {"type": "api", "name": "deepseek-chat"},
            "Qwen": {"type": "api", "name": "Qwen/Qwen2.5-14B-Instruct"},
            "Deepseek-R1-LAN": {"type": "lan", "name": "deepseek/deepseek-r1-0528-qwen3-8b"},
            "Qwen3.0-LAN": {"type": "lan", "name": "qwen/qwen3-4b"},
            "Qwen2.5-VL-LAN": {"type": "lan", "name": "qwen2.5-vl-instruct"},
            "Qwen2.5-Omni-LAN": {"type": "lan", "name": "qwen2.5-omni-instruct"},
            "Gemma3-LAN": {"type": "lan", "name": "google/gemma-3-4b"},
            "Deepseek-R1-Local": {"type": "local", "name": "deepseek/deepseek-r1-0528-qwen3-8b"},
            "Qwen3.0-Local": {"type": "local", "name": "qwen/qwen3-4b"},
            "Qwen2.5-VL-Local": {"type": "local", "name": "qwen2.5-vl-instruct"},
            "Qwen2.5-Omni-Local": {"type": "local", "name": "qwen2.5-omni-instruct"},
            "Gemma3-Local": {"type": "local", "name": "google/gemma-3-4b"}
        }
        
        # 攻防模拟场景列表
        self.attack_scenarios = [
            "Web应用SQL注入", "跨站脚本攻击(XSS)", "命令注入", "权限提升", 
            "敏感信息泄露", "SSRF服务器请求伪造", "XXE外部实体注入",
            "反序列化漏洞", "文件上传漏洞", "密码爆破", "中间人攻击", "会话劫持"
        ]
    
    def deepseek_request(self, messages, temperature=0.7, max_tokens=2000):
        """
        使用Deepseek API发送请求
        
        参数:
        - messages: 消息列表
        - temperature: 温度参数
        - max_tokens: 最大生成token数
        
        返回:
        - 生成的文本响应
        """
        # 每次请求前检查API密钥并更新客户端
        if not hasattr(self, 'deepseek_api_key') or not self.deepseek_api_key:
            print("Deepseek API配置不可用，请检查API密钥")
            return "Deepseek API密钥未配置，请在环境变量中设置DEEPSEEK_API_KEY"
        
        # 重新初始化客户端确保使用最新的API密钥
        self.deepseek_client = OpenAI(
            api_key=self.deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
            
        try:
            print("正在向Deepseek API发送请求...")
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            print(f"收到Deepseek API响应: {str(response)[:100]}...")
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                print("Deepseek API响应格式错误")
                return "Deepseek API响应格式错误"
        except Exception as e:
            print(f"Deepseek API请求失败: {str(e)}")
            return f"Deepseek API请求失败: {str(e)}"
    
    def qwen_request(self, messages, temperature=0.7, max_tokens=2000):
        """
        使用硅基流动Qwen API发送请求
        
        参数:
        - messages: 消息列表
        - temperature: 温度参数
        - max_tokens: 最大生成token数
        
        返回:
        - 生成的文本响应
        """
        # 每次请求前检查API密钥并更新headers
        if not hasattr(self, 'qwen_api_key') or not self.qwen_api_key:
            print("硅基流动API配置不可用，请检查API密钥")
            return "硅基流动API密钥未配置，请在环境变量中设置QWEN_API_KEY"
        
        # 更新headers确保token是最新的
        self.qwen_headers = {
            "Authorization": f"Bearer {self.qwen_api_key}",
            "Content-Type": "application/json"
        }
        self.qwen_url = "https://api.siliconflow.cn/v1/chat/completions"
            
        try:
            print("正在向硅基流动API发送请求...")
            payload = {
                "model": "Qwen/Qwen2.5-14B-Instruct",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = requests.post(
                self.qwen_url,
                headers=self.qwen_headers,
                json=payload,
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"硅基流动API请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return f"硅基流动API请求失败: 状态码 {response.status_code}"
                
            result = response.json()
            print(f"收到硅基流动API响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            else:
                print(f"硅基流动API响应格式错误: {result}")
                return "硅基流动API响应格式错误"
        except requests.Timeout:
            print("硅基流动API请求超时")
            return "硅基流动API请求超时"
        except Exception as e:
            print(f"硅基流动API请求失败: {str(e)}")
            return f"硅基流动API请求失败: {str(e)}"

    def get_model_request(self, messages, model_option="Qwen3.0-Local", model_name=None):
        """通用模型请求方法"""
        # 如果提供了模型选项，使用选项映射
        if model_option in self.model_options:
            model_config = self.model_options[model_option]
            model_type = model_config["type"]
            model_name = model_config["name"]
        elif not model_name:
            # 默认使用第一个支持的模型
            model_type = "local"
            model_name = self.supported_models[model_type][0]
        
        # 特殊处理API调用
        if model_option == "Deepseek-R1":
            return self.deepseek_request(messages)
        elif model_option == "Qwen":
            return self.qwen_request(messages)
            
        try:
            url = self.local_url if model_type == "local" else self.lan_url
            print(f"正在向{model_type}的{model_name}模型发送请求...")
            
            response = requests.post(
                url,
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"{model_type}的{model_name}请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return f"{model_name}模型离线不可用，请检查{model_type}服务是否正常运行"
                
            result = response.json()
            print(f"收到{model_type}的{model_name}模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"{model_name}模型错误: {result}")
                return f"{model_name}模型未找到或出现错误"
            else:
                print(f"{model_name}响应格式错误: {result}")
                return f"{model_name}响应格式错误，请检查模型输出"
        except requests.Timeout:
            print(f"{model_type}的{model_name}请求超时")
            return f"{model_name}请求超时，请检查服务是否正常运行"
        except requests.ConnectionError:
            print(f"无法连接到{model_type}的{model_name}服务")
            return f"{model_name}离线不可用，请检查服务是否正常运行"
        except Exception as e:
            print(f"{model_type}的{model_name}请求错误: {str(e)}")
            return f"{model_name}请求发生错误: {str(e)}"

    def generate_dynamic_scenario(self, difficulty="Medium", category="Web", context=None, model_option="Qwen3.0-Local"):
        """
        动态场景生成：自动生成与真实业务相关的多维攻防场景
        
        参数:
        - difficulty: 难度级别 (Easy, Medium, Hard, Expert)
        - category: 题目类别 (Web, Crypto, Reverse, Pwn, Forensics, Misc)
        - context: 可选的上下文信息，可以包含特定业务或技术要求
        - model_option: 使用的模型选项，默认为本地Qwen3.0
        
        返回:
        - 一个包含场景详情的字典
        """
        prompt = f"""
        作为一个网络安全CTF靶场系统，请生成一个真实的{category}类别、{difficulty}难度的攻防场景。
        
        场景要求:
        1. 贴近真实业务场景，与实际企业安全环境相似
        2. 包含详细的背景故事和目标
        3. 提供完整的技术细节，包括系统架构、使用的技术栈、存在的漏洞点
        4. 设计合理的攻击路径和多个解题步骤
        5. 生成适合的flag格式和隐藏位置
        
        请以JSON格式返回，包含以下字段:
        - title: 场景标题
        - description: 详细场景描述
        - background_story: 背景故事
        - technical_details: 技术细节
        - attack_paths: 可能的攻击路径
        - hints: 3-5个由易到难的提示
        - flag: flag字符串
        - solution: 完整解题思路
        - difficulty_score: 1-100的难度评分
        - skills_required: 所需技能列表
        """
        
        if context:
            prompt += f"\n\n额外上下文: {context}"
        
        messages = [{"role": "user", "content": prompt}]
        response = self.get_model_request(messages, model_option=model_option)
        
        try:
            # 尝试解析JSON响应
            scenario = json.loads(response)
            return scenario
        except json.JSONDecodeError:
            # 如果返回的不是有效JSON，则进行简单处理后返回
            return {
                "title": f"动态{category}场景 - {datetime.now().strftime('%Y%m%d%H%M')}",
                "description": response[:500] + "...(内容过长已截断)",
                "flag": f"flag{{{random.randint(10000, 99999)}}}",
                "error": "生成的场景格式不符合要求，请重新生成",
                "raw_response": response[:1000] + "...(内容过长已截断)"
            }

    def simulate_attack(self, scenario_data, target_info=None, attack_level="basic", model_option="Qwen3.0-Local"):
        """
        智能攻击模拟：通过攻击AI Agent模拟复杂的攻击链
        
        参数:
        - scenario_data: 场景数据，包含技术细节等
        - target_info: 目标系统信息
        - attack_level: 攻击复杂度 (basic, advanced, apt)
        - model_option: 使用的模型选项，默认为本地Qwen3.0
        
        返回:
        - 攻击模拟结果和攻击路径
        """
        attack_type = random.choice(self.attack_scenarios)
        
        prompt = f"""
        作为一个网络安全攻击模拟AI，请模拟针对以下目标系统的{attack_level}级别{attack_type}攻击过程。
        
        目标系统信息:
        {json.dumps(scenario_data, ensure_ascii=False, indent=2)}
        
        请详细描述:
        1. 完整的攻击链路和步骤
        2. 每个步骤的技术原理和利用方式
        3. 可能的攻击后果和影响范围
        4. 在攻击过程中可能遇到的防御措施和绕过方法
        
        根据攻击过程，分析出最有可能成功的获取flag的方法。
        """
        
        if target_info:
            prompt += f"\n\n额外的目标信息: {target_info}"
        
        messages = [{"role": "user", "content": prompt}]
        attack_simulation = self.get_model_request(messages, model_option=model_option)
        
        return {
            "attack_type": attack_type,
            "attack_level": attack_level,
            "timestamp": datetime.now().isoformat(),
            "simulation_result": attack_simulation,
            "success_probability": random.randint(30, 95)
        }

    def adaptive_defense(self, attack_data, system_config=None, defense_level="standard", model_option="Qwen3.0-Local"):
        """
        自适应防御决策：防御AI Agent动态优化安全策略
        
        参数:
        - attack_data: 攻击数据，包含攻击类型和路径
        - system_config: 当前系统配置
        - defense_level: 防御级别 (basic, standard, advanced)
        - model_option: 使用的模型选项，默认为本地Qwen3.0
        
        返回:
        - 防御策略和安全建议
        """
        prompt = f"""
        作为一个网络安全防御AI，请针对以下攻击情况，制定{defense_level}级别的防御策略和修复方案:
        
        攻击信息:
        {json.dumps(attack_data, ensure_ascii=False, indent=2)}
        
        请详细描述:
        1. 漏洞原因分析和风险评估
        2. 短期紧急防御措施
        3. 中长期修复方案
        4. 安全最佳实践建议
        5. 配置文件、代码修改等具体修复步骤
        
        防御策略应考虑实施成本、对业务影响和安全有效性等多方面因素，提供分层防御方案。
        """
        
        if system_config:
            prompt += f"\n\n系统当前配置: {system_config}"
        
        messages = [{"role": "user", "content": prompt}]
        defense_result = self.get_model_request(messages, model_option=model_option)
        
        return {
            "defense_level": defense_level,
            "timestamp": datetime.now().isoformat(),
            "defense_strategy": defense_result,
            "estimated_effectiveness": random.randint(60, 98)
        }

    def generate_evaluation_report(self, user_data, challenge_data, submission_history, model_option="Qwen3.0-Local"):
        """
        演练评估自动化：构建量化模型，自动生成演练评估报告
        
        参数:
        - user_data: 用户数据
        - challenge_data: 挑战数据
        - submission_history: 提交历史
        - model_option: 使用的模型选项，默认为本地Qwen3.0
        
        返回:
        - 评估报告和能力画像
        """
        prompt = f"""
        作为一个网络安全训练评估系统，请分析以下用户在CTF挑战中的表现，生成专业的能力评估报告:
        
        用户信息:
        {json.dumps(user_data, ensure_ascii=False, indent=2)}
        
        挑战信息:
        {json.dumps(challenge_data, ensure_ascii=False, indent=2)}
        
        提交历史:
        {json.dumps(submission_history, ensure_ascii=False, indent=2)}
        
        请在报告中包含:
        1. 整体能力评分(1-100)和水平定位
        2. 各安全领域的能力雷达图数据(Web安全、密码学、逆向工程、二进制利用、取证分析等)
        3. 技能强项和弱项分析
        4. 针对性的学习和提升建议
        5. 适合该用户的下一阶段挑战推荐
        
        评估应基于解题速度、正确率、使用提示情况、难度系数等多维度指标。
        """
        
        messages = [{"role": "user", "content": prompt}]
        evaluation_result = self.get_model_request(messages, model_option=model_option)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "evaluation_report": evaluation_result,
            "version": "1.0"
        }
    
    def suggest_challenge_solution(self, challenge_data, partial_solution=None, model_option="Qwen3.0-Local"):
        """
        提供题目解决方案建议
        
        参数:
        - challenge_data: 挑战数据
        - partial_solution: 部分解决方案或用户已尝试的方法
        - model_option: 使用的模型选项，默认为本地Qwen3.0
        
        返回:
        - 解决方案建议
        """
        prompt = f"""
        作为一个网络安全专家，请针对以下CTF挑战题目，提供解题思路和方法:
        
        挑战信息:
        {json.dumps(challenge_data, ensure_ascii=False, indent=2)}
        
        请提供:
        1. 挑战分析和核心漏洞/问题识别
        2. 逐步解题思路，从基础方法到进阶技巧
        3. 相关的工具使用建议
        4. 获取flag的具体方法
        
        请注意不要直接给出完整的解题步骤，而是提供启发性的引导和思路，帮助用户自己解决问题。
        """
        
        if partial_solution:
            prompt += f"\n\n用户已尝试的方法: {partial_solution}\n请基于用户的尝试给出更有针对性的建议。"
        
        messages = [{"role": "user", "content": prompt}]
        solution_suggestion = self.get_model_request(messages, model_option=model_option)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "solution_suggestion": solution_suggestion
        }

# 测试代码
if __name__ == "__main__":
    ctf_ai = CTFSecurityAI()
    
    # 测试场景生成
    scenario = ctf_ai.generate_dynamic_scenario(difficulty="Medium", category="Web")
    print("生成的场景:", json.dumps(scenario, ensure_ascii=False, indent=2))
    
    # 测试攻击模拟
    attack_result = ctf_ai.simulate_attack(scenario)
    print("攻击模拟结果:", json.dumps(attack_result, ensure_ascii=False, indent=2))
    
    # 测试防御决策
    defense_result = ctf_ai.adaptive_defense(attack_result)
    print("防御决策结果:", json.dumps(defense_result, ensure_ascii=False, indent=2)) 