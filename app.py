from flask import Flask, request
import time

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
    def __eq__(self, __value: object) -> bool:
        return self.username == __value.username and self.password == __value.password

class Fight:
    def __init__(self, user1: User, user2: User):
        self.user1 = user1
        self.user2 = user2
        self.score1 = 0
        self.score2 = 0
        self.finished1 = False
        self.finished2 = False
        self.last_update = time.time()
    def __contains__(self, __value: object) -> bool:
        return self.user1 == __value or self.user2 == __value

    def sync_score(self, user: User, score: int) -> int:
        self.last_update = time.time()
        if user == self.user1:
            self.score1 = score
            return self.score2
        elif user == self.user2:
            self.score2 = score
            return self.score1
        else:
            raise Exception("User not in fight")

class Record:
    def __init__(self, name: User, score: int, record_id: int, date: str):
        self.name = name
        self.score = score
        self.record_id = record_id
        self.date = date

users = [
    User('admin', 'admin'),
    User('user1', 'pass1'),
    User('user2', 'pass2'),
]

waiting_list = []
fighting_list: list[Fight] = []
rank_list = []

records = []

app = Flask(__name__)

@app.post("/login")
def login():
    username = request.form['username']
    password = request.form['password']
    if User(username, password) in users:
        print(f"{username} login")
        return {"status": "success"}
    return {"status": "failed", "reason": "wrong username or password"}

@app.post("/en_queue")
def en_queue():
    clear_fight()
    username = request.form['username']
    password = request.form['password']
    user = User(username, password)
    for fight in fighting_list:
        if user in fight:
            return {"status": "success"}
    if user in waiting_list:
        return {"status": "success"}
    waiting_list.append(user)
    print(f"{username} en_queue")
    if len(waiting_list) >= 2:
        user1 = waiting_list.pop(0)
        user2 = waiting_list.pop(0)
        fighting_list.append(Fight(user1, user2))
        print("{} vs {}".format(user1.username, user2.username))
    return {"status": "success"}

@app.post("/check_fighting")
def check_fighting():
    clear_fight()
    username = request.form['username']
    password = request.form['password']
    user = User(username, password)
    for fight in fighting_list:
        if user in fight:
            return {"status": "success"}
    if user in waiting_list:
        return {"status": "waiting"}
    return {"status": "failed", "reason": "not in queue"}

@app.post("/sync_score")
def sync_score():
    username = request.form['username']
    password = request.form['password']
    score = int(request.form['score'])
    
    user = User(username, password)
    for fight in fighting_list:
        if user in fight:
            opponent_score = fight.sync_score(user, score)
            break
    else:
        return {"status": "failed", "reason": "not in fighting"}
    return {"status": "success", "opponent_score": opponent_score}

@app.post("/finish")
def finish():
    username = request.form['username']
    password = request.form['password']
    
    user = User(username, password)
    for fight in fighting_list:
        if user in fight:
            print("{} finish".format(user.username))
            if user == fight.user1:
                fight.finished1 = True
                score = fight.score1
            else:
                fight.finished2 = True
                score = fight.score2
            
            records.append(Record(user.username, score, len(records), str(int(time.time()*1000))))
            
            if fight.finished1 and fight.finished2:
                fighting_list.remove(fight)
                print("{} vs {} finished".format(fight.user1.username, fight.user2.username))
            break
    else:
        return {"status": "failed", "reason": "not in fighting"}
    return {"status": "success"}

@app.get("/get_records")
def get_records():
    username = request.form['username']
    password = request.form['password']
    
    user = User(username, password)
    if user not in users:
        return {"status": "failed", "reason": "wrong username or password"}
    return {"status": "success", "records": records}

def clear_fight():
    global fighting_list
    fighting_list = [fight for fight in fighting_list if time.time() - fight.last_update < 60]

if __name__ == "__main__":
    app.run(port=7000, debug=True)