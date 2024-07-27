from core.QuestionHandler import QuestionHandler
from configs import LLM_MODEL
class ChatHandler:
    def __init__(self,endpoint,endpoint_t_box,t_box_index,normalizer,a_box_index=None):
        self.chats = {}
        self.endpoint = endpoint
        self.endpoint_t_box = endpoint_t_box
        self.t_box_index = t_box_index
        self.normalizer = normalizer
        self.a_box_index = a_box_index
        self.questions = {}
    
    def getChat(self,id) -> QuestionHandler:
        if id in self.chats:
            return self.chats[id]
        else:
            qa = QuestionHandler(self.endpoint,self.endpoint_t_box,self.t_box_index,self.normalizer,a_box_index=self.a_box_index,model_name=LLM_MODEL)
            self.chats[id] = qa
            return qa
        
    def get_last_question(self,user_id):
        if not user_id in self.questions:
            return None
        return self.questions[user_id]
    
    def add_question(self,user_id,question):
        self.questions[user_id] = question

    
    def process_question(self,user_id,question):
        qa = self.getChat(user_id)
        last_question = self.get_last_question(user_id)
        result = qa.processQuestion(question,last_question=last_question)
        self.add_question(user_id,question)

        return result