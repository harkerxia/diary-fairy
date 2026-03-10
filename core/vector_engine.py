from sentence_transformers import SentenceTransformer, util
import torch

class IntentRouter:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.retrieve_examples = [
            "我以前说过什么", "查一下我之前的笔记", 
            "回忆一下关于...的事情", "根据我的架构草案",
            "那个qmd文件里写了什么", "我想起上次我们聊过",
            "翻一下我过去的计划", "我之前的配置是怎么写的",
            "检索一下相关的技术文档", "帮我看看去年的总结",
            "我记得我跟你提过这个需求", "根据我存入的资料库回答",
            "关于那个项目的背景信息", "查询一下我的备忘录",
            "参考我发给你的代码片段", "搜索一下关于这方面的记录"
        ]
        self.example_embeddings = self.model.encode(self.retrieve_examples, convert_to_tensor=True)

    def should_retrieve(self, user_input):
        input_embedding = self.model.encode(user_input, convert_to_tensor=True)
        cosine_scores = util.cos_sim(input_embedding, self.example_embeddings)
        max_score = torch.max(cosine_scores).item()
        
        return max_score > 0.45