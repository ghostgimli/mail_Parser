import extract_msg
import io
import os

class MSG_worker:
    def __init__(self, users=[''], user_file='users.txt', ch_usr='', usr=''):
        self.users = users
        self.user_file = user_file
        self.ch_usr = ch_usr
        self.usr = usr

    @staticmethod
    def parse_users(file):
        with io.open(file, "r",encoding="utf-8") as usr_file:
            users = [item for item in usr_file.readlines() if (item is not None and item != '\n')]
        return users

    def save_file(self,file,input):
        with io.open(file,'w',encoding="utf-8") as f:
            for item in input:
                f.write(item+'\n')
            f.close()
    #'users.txt'

    def set_users_file(self):
        if self.ch_usr == 'add':
            self.users.append(self.usr)
        elif self.ch_usr == 'del':
            self.users.remove(self.usr)
        else:
            return -1
        self.save_file(self.user_file,self.users)
        return 0

    def extract_file(self,new_file):
        msgs = [ x for x in os.listdir() if '.msg' in x]
        result = []
        for msg in msgs:
            text = extract_msg.Message(msg).body.split('\n')
            for row in text:
                for x in self.users:
                    if x in row:
                        result.append(row)
        self.save_file(new_file,result)




                #output = "".join([x for x in text if ])
