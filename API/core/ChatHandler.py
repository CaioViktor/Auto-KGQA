from core.QuestionHandler import QuestionHandler
class ChatHandler:
    def __init__(self,endpoint,t_box_index,normalizer,a_box_index=None):
        self.chats = {}
        self.endpoint = endpoint
        self.t_box_index = t_box_index
        self.normalizer = normalizer
        self.a_box_index = a_box_index
    
    def getChat(self,id) -> QuestionHandler:
        if id in self.chats:
            return self.chats[id]
        else:
            qa = QuestionHandler(self.endpoint,self.t_box_index,self.normalizer,a_box_index=self.a_box_index)
            self.chats[id] = qa
            return qa