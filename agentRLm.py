import qlearn
import random
import pickle
import sys
# import matplotlib.pyplot as plt

# white 0, black 1, empty 2
# instatus 1: able to read, 2 Black win by five , 3 Black lose by five, 4 Black forbid move

stepHistory = []

def backupStep(lastState, lastAction, reward, state):
    stepHistory.append((lastState, lastAction, reward, state))

class Agent:
    def __init__(self, side, width=None, height=None, infilename=None, outfilename=None):
        if width is None:
            width = 15
        if height is None:
            height = 15
        if infilename is None:
            infilename = "input.txt"
        if outfilename is None:
            outfilename = "output.txt"

        self.side = side
        self.width = width
        self.height = height
        self.infilename = infilename
        self.outfilename = outfilename
        self.instatus = '-1'  # 1:able , -1:disable
        self.outstatus = '-1' # 1:able , -1:disable
        self.first = None
        self.input = []
        self.inputT = ()
        self.nextmove = -1
        self.reward = 0
        self.gamenum = 0
        self.posnum = 0
        self.winnum = 0
        self.losenum = 0
        self.drawnum = 0
        self.winflag = 0
        self.ai = None
        # how to set action?
        self.ai = qlearn.QLearn(side=self.side, width=self.width, height=self.height, actions=range(self.height*self.width), alpha=0.1, gamma=0.9, epsilon=0.01)
        self.lastAction = None
        self.lastState = None
        self.hist = []

        # for graph
        self.reward_list = []
        self.epi_list = []
        self.posnum_list = []

    def readPlate(self):
        while True:
            fin = open(self.infilename,"r")
            self.instatus = fin.readline()[:-1]
            if self.instatus >= '1':
                self.input = fin.read().splitlines()
                fin.close()
                break

            fin.close()

        if self.instatus == '1':
            fin = open(self.infilename, "w")
            fin.write('-1')
            fin.write('\n')
            for i in range(self.height):
                for j in range(self.width):
                    fin.write(self.input[i * self.height + j])
                    fin.write('\n')
            fin.close()

    def writePlate(self):
        while True:
            fout = open(self.outfilename,"r")
            self.outstatus = fout.readline()[:-1]
            if self.outstatus == '1':
                fout.close()
                break
            fout.close()

        self.outstatus = '-1'
        fout = open(self.outfilename, "w")
        fout.write(self.outstatus)
        fout.write('\n')
        data = '%d %d' %(self.nextmove ,self.side)
        fout.write(data)
        fout.close()

    def nextMove(self):
        flag = 0
        for i in range(self.height*self.width):
            if self.input[i] != '2':
                flag = 1
                break
        #print 'flag : %d' %flag
        if flag == 1:
            while True:
                index = random.randint(0, self.height*self.width-1)
                if self.input[index] == '2':
                    self.nextmove = index
                    break
        else:
            self.nextmove = self.height * self.width / 2

        self.posnum += 1
        #print 'nextmove : %d' %self.nextmove

    # instatus 1: able to read, 2 Black win by five , 3 Black lose by five, 4 Black forbid move, 5 draw
    def getresult(self):
        flag = 0
        if self.instatus == '2':
            if self.side == 1: # AI Win
                self.reward = 200
                self.winnum += 1
                self.winflag = 1
            else:
                self.reward = -300
                self.losenum += 1
                self.winflag = -1
            self.gamenum += 1
            flag = 1

        if self.instatus == '3':
            if self.side == 0: # AI Win
                self.reward = 200
                self.winnum += 1
                self.winflag = 1
            else:
                self.reward = -300
                self.losenum += 1
                self.winflag = -1
            self.gamenum += 1
            flag = 1

        if self.instatus == '4':
            if self.side == 1:      # invalid move
                self.reward = -300
                self.losenum += 1
                self.winflag = -1
            else:
                self.reward = 200
                self.winnum += 1
                self.winflag = 1
            self.gamenum += 1
            flag = 1

        if self.instatus == '5':    # draw
            self.reward = 10
            self.gamenum += 1
            self.drawnum += 1
            self.winflag = 2
            flag = 1

        #if self.posnum <= 5:
        #    self.reward = -50

        #if self.posnum >= 10:
        #    self.reward = +5

        if flag == 1:
            if self.winflag == 2:
                fre = open("result.txt", "a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f draw' % (
                self.gamenum, self.posnum, self.winnum, winrate))
                fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f draw' % (
                self.gamenum, self.posnum, self.winnum, winrate)
                fre.close()
            if self.winflag == 1:
                fre = open("result.txt","a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f win' %(self.gamenum,self.posnum,self.winnum,winrate))
                fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f win' %(self.gamenum,self.posnum,self.winnum,winrate)
                fre.close()
                # self.saveResult()
            if self.winflag == -1:
                fre = open("result.txt","a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f lose' % (self.gamenum,self.posnum,self.winnum,winrate))
                fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f lose' % (self.gamenum,self.posnum,self.winnum,winrate)
                # fre.close()
        return flag

    def newGame(self):
        self.posnum = 0
        self.reward = 0
        self.lastAction = None
        self.lastState = None
        self.first = None
        self.first = True
        self.hist = None
        self.hist = []
        fin = open(self.infilename, "w")
        fout = open(self.outfilename, "w")

        fin.write('1')
        fin.write('\n')
        for i in range(self.height*self.width):
            fin.write('2')
            fin.write('\n')
        fout.write('1')
        fout.write('\n')
        fin.close()
        fout.close()

    def learn(self):
        for j in range(100):
            for i in self.hist:
                tu = i
                if tu[3] == 200 or tu[3] == -300:   # win or lose
                    self.ai.learn(tu[0], tu[1], tu[3], tu[2])
                elif tu[3] == 10:   # draw
                    self.ai.learn(tu[0], tu[1], 0, tu[2])
                else:
                    self.ai.learn(tu[0], tu[1], -1, tu[2])

    def update(self):
        #how to set state? tuple?
        self.inputT = ()
        self.dict_input = ()
        for i in range(self.height*self.width):
            b = ()
            c = ()
            b = self.input[i],
            if self.input[i] == '1': # black -> positive
                c = i,
            elif self.input[i] == '0': # white -> negative
                c = -i,

            self.inputT = self.inputT + b
            self.dict_input = self.dict_input + c

        state = self.inputT
        dict_state = self.dict_input
        reward = self.reward
        # how to set action init?
        if self.first == True:
            action = self.height*self.width/2
            self.first = False
        elif self.winflag == 2:
            action = None
        else:
            action = self.ai.chooseAction(state, dict_state)
        if self.lastAction is not None:
            #self.ai.alpha = 1/((2*self.posnum)+1)
            # print self.lastState
            # print self.lastAction
            # print reward
            # print dict_state
            # print 'end'
            # self.ai.learn(self.lastState, self.lastAction, reward, dict_state)
            tu = (self.lastState, self.lastAction, dict_state, reward)
            self.hist.append(tu)

        self.lastState = dict_state
        self.lastAction = action
        #backupStep(self.lastState, self.lastAction, reward, dict_state)
        self.nextmove = action
        self.posnum += 1

    def saveResult(self):
        f1 = open("win_black.txt", "a")
        for i in range(self.height):
            for j in range(self.width):
                f1.write(self.input[i * self.width + j])
                f1.write(' ')
            f1.write('\n')
        f1.write('nextmove : %d' %self.nextmove)
        f1.write('\n')
        f1.close()

    def priorInfo(self):
        fr = open("data.txt","r")
        while True:
            line = fr.readline()
            if not line:
                break
            self.info = line.strip().split(' ')
            line = fr.readline()
            self.in_status = int(line)
            self.priorlearn(self.info, self.in_status)
            self.newGame()

        print 'learn data end'

    def priorlearn(self, action_list, result):
        hist_order = []
        temp_state = []
        last_State = None
        last_Action = None
        for i in range(self.height*self.width):
            temp_state.append(2)

        for i in range(len(action_list)):
            reward = 0
            if i == len(action_list) - 1:  # last learn if black
                if last_Action is not None:
                        temp_tu = (last_State, last_Action, self.dict_input)
                        hist_order.append(temp_tu)
                        # self.ai.learn(last_State, last_Action, reward, self.dict_input) // set last turn result

                if result == 2:
                    if self.side == 1:  # AI Win
                        reward = 10
                    else:
                        reward = -100

                if result == 3:
                    if self.side == 0:  # AI Win
                        reward = 10
                    else:
                        reward = -100

                if result == 4:
                    if self.side == 1:
                        reward = -100

                if result == 5:  # draw
                    reward = 8

                # if self.posnum > 6:
                #     reward = 5

                last_Action = int(action_list[i])
                self.dict_input = ()
                for j in range(self.height * self.width):
                    c = ()
                    if temp_state[j] == 1:  # black -> positive
                        c = j,
                    elif temp_state[j] == 0:  # white -> negative
                        c = -j,
                    self.dict_input = self.dict_input + c

                last_State = self.dict_input    # set last_State
                temp_state[int(action_list[i])] = 1  # set black move

                self.dict_input = ()
                for j in range(self.height * self.width):
                    c = ()
                    if temp_state[j] == 1:  # black -> positive
                        c = j,
                    elif temp_state[j] == 0:  # white -> negative
                        c = -j,
                    self.dict_input = self.dict_input + c   # set dict_input ->> state

                if len(action_list)%2 != 0:
                    temp_tu = (last_State, last_Action, self.dict_input)
                    hist_order.append(temp_tu)
                    # self.ai.learn(last_State, last_Action, reward, self.dict_input) // set last turn result

            elif i%2 == 0:  # black move
                if last_Action is not None:
                    temp_tu = (last_State, last_Action, self.dict_input)
                    hist_order.append(temp_tu)
                    # self.ai.learn(last_State, last_Action, reward, self.dict_input)

                last_Action = int(action_list[i])
                self.dict_input = ()
                for j in range(self.height*self.width):
                    c = ()
                    if temp_state[j] == 1:  # black -> positive
                        c = j,
                    elif temp_state[j] == 0:  # white -> negative
                        c = -j,
                    self.dict_input = self.dict_input + c

                last_State = self.dict_input
                temp_state[int(action_list[i])] = 1  # set black first move

            elif i%2 == 1: # white move
                temp_state[int(action_list[i])] = 0 # set white second move
                self.dict_input = ()
                for j in range(self.height*self.width):
                    c = ()
                    if temp_state[j] == 1:  # black -> positive
                        c = j,
                    elif temp_state[j] == 0:  # white -> negative
                        c = -j,
                    self.dict_input = self.dict_input + c

        for i in hist_order:
            tu = i
            if result == 2: # black win
                self.ai.learn(tu[0], tu[1], 1, tu[2])
            elif result == 3:  # white win
                self.ai.learn(tu[0], tu[1], -1, tu[2])
            else: # draw
                self.ai.learn(tu[0], tu[1], 0.5, tu[2])

    def init_graph(self):
        self.reward_list = []
        self.epi_list = []

    def set_graph(self, reward, epi, pos):
        self.reward_list.append(reward)
        self.epi_list.append(epi)
        self.posnum_list.append(pos)

    def save_graph(self):
        print 'save graph'
        with open('reward_list.txt', 'w') as fr:
            pickle.dump(self.reward_list, fr)
        with open('epi_list.txt', 'w') as fe:
            pickle.dump(self.epi_list, fe)
        with open('posnum_list.txt', 'w') as fd:
            pickle.dump(self.posnum_list, fd)
        fr.close()
        fe.close()
        fd.close()

    # def make_graph_reward(self):
    #     plt.plot(self.epi_list, self.reward_list, 'r')
    #     plt.xlabel('episode')
    #     plt.ylabel('reward')
    #     plt.savefig('episode-reward.png'.format(0))
    #     print 'make graph'

    def set_epsilon(self):
        self.ai.epsilon = 0.1

def main():
    agent = Agent(side=1, width=15, height=15)
    agent.newGame()
    agent.init_graph()

    # iter = 0
    # while iter < 10000:
    #     agent.priorInfo()
    #     agent.newGame()
    #     iter = iter + 1
    #     if(iter % 10 == 0):
    #         agent.ai.saveRe(iter)
    #
    # agent.ai.saveQ()

    epi = 0
    try:
        while True:
            agent.winflag = 0
            agent.readPlate()
            flag = agent.getresult()
            if flag == 0:
                agent.update()
                agent.writePlate()
            else:
                agent.update()
                agent.learn()
                # r = agent.ai.get_reward()
                # r = r / agent.posnum
                # if r != 0:
                #     epi = epi+1
                #     agent.set_graph(r, epi)
                # agent.ai.init_reward()
                r = (float(agent.winnum) / float(agent.gamenum) * 100)
                epi = epi+1
                agent.set_graph(r, epi, agent.posnum)
                agent.newGame()
                if agent.first == False:
                    agent.first = True

                if agent.gamenum >= 500000:
                    if agent.gamenum % 500000 == 0:
                        agent.ai.saveQ()
                        agent.save_graph()

            if agent.gamenum > 1000000:
                print 'final (gamenum,winrate) : (%d, %f)' %(agent.gamenum, (float(agent.winnum) / float(agent.gamenum) * 100))
                # agent.make_graph_reward()
                agent.ai.saveQ()
                agent.save_graph()
                break

    except KeyboardInterrupt:
        print 'except --------- '
        agent.ai.saveQ()
        agent.save_graph()

if __name__ == "__main__":
    main()
