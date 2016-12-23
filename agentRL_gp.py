import numpy as np

from gpsarsa import GPTDController
import random
import sys

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

        initial_state = np.zeros(self.height*self.width)
        initial_state.fill(2)
        initial_action = self.height*self.width/2
        self.ai = GPTDController(initial_state, initial_action)
        self.lastAction = None
        self.lastState = None

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
                    fin.write(self.input[i * self.width + j])
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
        for i in range(self.height * self.width):
            if self.input[i] != '2':
                flag = 1
                break
        #print 'flag : %d' %flag
        if flag == 1:
            while True:
                index = random.randint(0, self.height * self.width - 1)
                if self.input[index] == '2':
                    self.nextmove = index
                    break
        else:
            self.nextmove = self.height * self.width / 2

        self.posnum += 1
        #print 'nextmove : %d' %self.nextmove

    # instatus 1: able to read, 2 Black win by five , 3 Black lose by five, 4 Black forbid move
    def getresult(self):
        flag = 0
        if self.instatus == '2':
            if self.side == 1: # AI Win
                self.reward = 10
                self.winnum += 1
                self.winflag = 1
            else:
                self.reward = -100
                self.losenum += 1
                self.winflag = -1
            self.gamenum += 1
            flag = 1

        if self.instatus == '3':
            if self.side == 0: # AI Win
                self.reward = 10
                self.winnum += 1
                self.winflag = 1
            else:
                self.reward = -100
                self.losenum += 1
                self.winflag = -1
            self.gamenum += 1
            flag = 1

        if self.instatus == '4':
            if self.side == 1:
                self.reward = -100
                self.gamenum += 1
                self.losenum += 1
                self.winflag = -1
                flag = 1

        if self.instatus == '5':
            self.reward = +5
            self.gamenum += 1
            self.drawnum += 1
            self.winflag = 2
            flag = 1

        if self.posnum <= 5:
           self.reward = -50

        if self.posnum >= 10:
           self.reward = +5

        if flag == 1:
            if self.winflag == 2:
                fre = open("result.txt", "a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f draw' % (self.gamenum, self.posnum, self.winnum, winrate))
                fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f draw' % (self.gamenum, self.posnum, self.winnum, winrate)
                fre.close()
            if self.winflag == 1:
                fre = open("result.txt","a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f win' %(self.gamenum,self.posnum,self.winnum,winrate))
                fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f win' %(self.gamenum,self.posnum,self.winnum,winrate)
                fre.close()
            if self.winflag == -1:
                fre = open("result.txt","a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                #fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f lose' % (self.gamenum,self.posnum,self.winnum,winrate))
                #fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f lose' % (self.gamenum,self.posnum,self.winnum,winrate)
                fre.close()
        return flag

    def newGame(self):
        self.posnum = 0
        self.reward = 0
        self.lastAction = None
        self.first = None
        self.first = True
        fin = open(self.infilename, "w")
        fout = open(self.outfilename, "w")

        fin.write('1')
        fin.write('\n')
        for i in range(self.height * self.width):
            fin.write('2')
            fin.write('\n')
        fout.write('1')
        fout.write('\n')
        fin.close()
        fout.close()

    def update(self):

        rinput = []
        for elm in self.input:
            rinput.append(int(elm))

        state = np.array(rinput)
        reward = self.reward
        # how to set action init?
        if self.first == True:
            action = self.height * self.width / 2
            self.first = False
        elif self.winflag == 2: # draw
            action = None
        else:
            action = self.ai.get_best_action(state)
        if self.lastAction is not None:
            if action is not None:
                #self.ai.alpha = 1/((2*self.posnum)+1)
                self.ai.observe_step(self.lastState, self.lastAction, reward, state, action)

        self.lastState = state
        self.lastAction = action
        #backupStep(self.lastState, self.lastAction, reward, state)
        self.nextmove = action
        self.posnum += 1

    def priorInfo(self):
        fr = open("data.txt", "r")
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
        temp_state = []
        last_State = None
        last_Action = None
        for i in range(self.height * self.width):
            temp_state.append(2)

        for i in range(len(action_list)):
            reward = 0
            if i == len(action_list) - 1:  # last learn
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

                temp_state[int(action_list[i])] = 1  # set black move
                state = np.array(temp_state)
                action = int(action_list[i])


                if last_Action is not None:
                    self.ai.observe_step(last_State, last_Action, reward, state, action)

            elif i % 2 == 0:  # black move
                temp_state[int(action_list[i])] = 1  # set black move
                state = np.array(temp_state)
                action = int(action_list[i])

                if last_Action is not None:
                    self.ai.observe_step(last_State, last_Action, reward, state, action)

                last_Action = action
                last_State = state


            elif i % 2 == 1:  # white move
                temp_state[int(action_list[i])] = 0  # set white second move

def main():
    agent = Agent(side=1, width=7, height=7)
    agent.newGame()

    # agent.priorInfo()
    # agent.newGame()
    # agent.ai.saveQ()
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
                agent.newGame()
                if agent.first == False:
                    agent.first = True

            if agent.gamenum > 10000:
                if agent.gamenum % 10000 == 0:
                    agent.ai.saveQ()

            if agent.gamenum > 2:
                print 'final (gamenum,winrate) : (%d,%f)' %(agent.gamenum,agent.winnum/agent.gamenum*100)
                agent.ai.saveQ()
                break

    except Exception as e:
        print e
        print 'except --------- '
        agent.ai.saveQ()


if __name__ == "__main__":
    main()
