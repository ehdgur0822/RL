import random
import pickle


class QLearn:
    def __init__(self, side, width, height, actions, epsilon=0.01, alpha=0.2, gamma=0.9):
        self.q = {}

        self.stepHistory = []
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions
        self.validactions = []
        self.width = width
        self.height = height
        self.side = side
        self.acc_q = 0
        try:
            if self.side == 0:
                with open('qvalue_w.txt', 'r') as f:
                    self.q = pickle.load(f)
                print 'q value load complete'
            else:
                with open('qvalue.txt','r') as f:
                    self.q = pickle.load(f)
                print 'q value load complete'

        except IOError:
            self.q = {}

    def getQ(self, state, action):
        return self.q.get((state, action), 0.0)

    # defines policy
    def chooseAction(self, state, dict_state):
            self.validactions = []
            self.min_x = self.width - 1
            self.max_x = 0
            self.min_y = self.height - 1
            self.max_y = 0
            self.temp_x = 0
            self.temp_y = 0
            for a in self.actions:
                if state[a] == '1' or state[a] == '0':
                    #self.validactions.append(a)
                    self.temp_x = a%self.width
                    self.temp_y = (a-self.temp_x)/self.height
                    #print 'temp %d %d' % (self.temp_x, self.temp_y)
                    if self.temp_x < self.min_x:
                        self.min_x = self.temp_x
                    if self.temp_x > self.max_x:
                        self.max_x = self.temp_x
                    if self.temp_y < self.min_y:
                        self.min_y = self.temp_y
                    if self.temp_y > self.max_y:
                        self.max_y = self.temp_y

            #print '1: %d %d %d %d' % (self.min_x, self.max_x, self.min_y, self.max_y)

            if self.min_x - 3 < 0:
                self.min_x = 0
            else:
                self.min_x -= 3

            if self.max_x + 3 > self.width - 1:
                self.max_x = self.width - 1
            else:
                self.max_x += 3

            if self.min_y - 3 < 0:
                self.min_y = 0
            else:
                self.min_y -= 3

            if self.max_y + 3 > self.height - 1:
                self.max_y = self.height - 1
            else:
                self.max_y += 3

            # print '2: %d %d %d %d' %(self.min_x, self.max_x, self.min_y, self.max_y)


            for i in range(self.min_y, self.max_y+1):
                for j in range(self.min_x, self.max_x+1):
                    a = self.width * i + j
                    if state[a] == '2':
                        self.validactions.append(a)

            if random.random() < self.epsilon:
                action = random.choice(self.validactions)
            else:
                q = [self.getQ(dict_state, a) for a in self.validactions]
                maxQ = max(q)
                self.acc_q = self.acc_q + maxQ
                count = q.count(maxQ)
                if count > 1:
                    best = [i for i in range(len(self.validactions)) if q[i] == maxQ]
                    i = random.choice(best)
                else:
                    i = q.index(maxQ)

                action = self.validactions[i]
            return action

    def learn(self, state1, action1, reward, state2):
        maxqnew = max([self.getQ(state2, a) for a in self.actions])
        oldv = self.q.get((state1, action1), None)
        if oldv is None:
            self.q[(state1, action1)] = reward
        else:
            # Q-learning formula
            # Q(S, A) <- Q(S, A) + alpha*[R + gamma*max(Q(S', a)) - Q(S, A)]
            self.q[(state1, action1)] = oldv + self.alpha * (reward + self.gamma * maxqnew - oldv)

    def saveQ(self):
        print 'saveQ'
        if self.side == 0:
            with open('qvalue_w.txt', 'wb') as f:
                pickle.dump(self.q, f)
        else:
            with open('qvalue.txt', 'wb') as f:
                pickle.dump(self.q, f)
        f.close()

    def saveRe(self,num):
        print 'saveRe'
        na = "qvalue"
        na += str(num)
        na += ".txt"

        with open(na, 'wb') as f:
                pickle.dump(self.q, f)
        f.close()
    
    def printQ(self):
        print self.q

    def init_reward(self):
        self.acc_q = 0

    def get_reward(self):
        return self.acc_q

# import math
def ff(f, n):
    fs = "{:f}".format(f)
    if len(fs) < n:
        return ("{:"+n+"s}").format(fs)
    else:
        return fs[:n]
