import pandas as pd
class Questions_Dataset:
    def __init__(self,path="questions_dataset.csv") -> None:
        self.path = path
        self.columns = ['id','question','answer','sparql','sparqls','fragments','correct','user_id']
        self.dataset = pd.DataFrame(columns=self.columns)

    @staticmethod
    def load(path):
        dataset = pd.read_csv(path)
        qd= Questions_Dataset(path)
        qd.dataset = dataset
        return qd
    
    def save(self):
        self.dataset.to_csv(self.path,columns=self.columns, index=False)
    
    def add(self,element,user_id='1'):
        ele = dict(element)
        if 'sparqls' in ele:
            ele['sparqls'] = str(ele['sparqls'])
        for column in self.columns:
            if not column in ele:
                ele[column] = ''
        ele['user_id'] = user_id
        if self.dataset.shape[0] > 0:
            last_id = self.dataset.iloc[-1]['id']
            ele['id']= str(int(last_id) + 1)
        else:
            ele['id'] = '1'
        new_row = pd.DataFrame([ele],columns=self.columns)
        self.dataset = pd.concat([self.dataset,new_row],ignore_index=True)
        self.dataset.reset_index()
        return ele
    
    def feedback(self,id_question,feedback = '1'):
        self.dataset.loc[self.dataset['id'] == id_question,'correct'] = feedback