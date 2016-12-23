import qlearn
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
        self.instatus = '1'  # -1:able , 1:disable
        self.outstatus = '1' # -1:able , 1:disable
        self.plate = []
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
        self.ai = qlearn.QLearn(side=self.side, width=self.width, height=self.height, actions=range(self.height*self.width), alpha=0.1, gamma=0.9, epsilon=0)
        self.lastAction = None
        self.lastState = None
        self.hist = []

    def printPlate(self):
        # p = 0
        # while p < 225:
        #     print (self.plate[p:p+15])
        #     p = p+15
        #
        # print '\n'
        print 'board'
        print 'abcdefghijklmno'
        for i in range(15):
            for j in range(15):
                p = i*15 + j
                c = self.plate[p]
                sys.stdout.write(c)
            sys.stdout.write('\n')
        sys.stdout.write('\n')
        # raw_input()

    def readPlate(self):
        while True:
            fout = open(self.outfilename,"r")
            self.outstatus= fout.readline()[:-1]
            if self.outstatus == '-1':
                blackmove = fout.readline()[:-1]
                fout.close()
                break

            fout.close()

        self.plate[int(blackmove)] = '1' # set black move

        if self.outstatus == '-1':
            fout = open(self.outfilename,"w")
            fout.write('1')
            fout.write('\n')
            fout.close()

    def writePlate(self):
        while True:
            fin = open(self.infilename,"r")
            self.instatus = fin.readline()[:-1]
            if self.instatus == '-1':
                fin.close()
                break
            fin.close()

        self.calcresult()

        fin = open(self.infilename, "w")
        fin.write(self.instatus)
        fin.write('\n')
        for i in range(len(self.plate)):
            fin.write(self.plate[i])
            fin.write('\n')
        fin.close()

    def nextMove(self):
        while True:
            index = random.randint(0, self.height*self.width-1)
            if self.input[index] == '2':
                self.nextmove = index
                break

        self.posnum += 1
        #print 'nextmove : %d' %self.nextmove

    # point:int, side:char
    def d1(self, point, side):   # right
        len = 0
        if self.plate[point] == side:
            len = len+1
            p = point+1
            while (p % self.width) < self.width and p < self.width*self.height:
                if self.plate[p] == side:
                    len = len+1
                    p = p+1
                else:
                    break

        return len

    def d2(self, point, side):   # dowm
        len = 0
        if self.plate[point] == side:
            len = len + 1
            p = point + 15
            while p < self.width * self.height:
                if self.plate[p] == side:
                    len = len + 1
                    p = p + 15
                else:
                    break

        return len

    def d3(self, point, side):   # right down
        len = 0
        if self.plate[point] == side:
            len = len + 1
            p = point + 16
            while p < self.width * self.height:
                if self.plate[p] == side:
                    len = len + 1
                    p = p + 16
                else:
                    break

        return len

    def d4(self, point, side):   # left down
        len = 0
        if self.plate[point] == side:
            len = len + 1
            p = point + 14
            while (p % self.width) < self.width and p < self.width * self.height:
                if self.plate[p] == side:
                    len = len + 1
                    p = p + 14
                else:
                    break

        return len

    # instatus 1: able to read, 2 Black win by five , 3 Black lose by five, 4 Black forbid move, 5 draw
    # set self.instatus
    def calcresult(self):
        self.instatus = '1' # initialize

        if self.posnum == 70:  # or self.width * self.height
            self.instatus = '5'
            return

        # find 5
        for i in range(225):
            if self.d1(i, '0') == 5:
                self.instatus = '3'
                return
            if self.d2(i, '0') == 5:
                self.instatus = '3'
                return
            if self.d3(i, '0') == 5:
                self.instatus = '3'
                return
            if self.d4(i, '0') == 5:
                self.instatus = '3'
                return
            if self.d1(i, '1') == 5:
                self.instatus = '2'
                return
            if self.d2(i, '1') == 5:
                self.instatus = '2'
                return
            if self.d3(i, '1') == 5:
                self.instatus = '2'
                return
            if self.d4(i, '1') == 5:
                self.instatus = '2'
                return

        # find 3-3
        for i in range(225):
            num = 0
            if self.d1(i, '1') == 3:
                num = num + 1
            if self.d2(i, '1') == 3:
                num = num + 1
            if self.d3(i, '1') == 3:
                num = num + 1
            if self.d4(i, '1') == 3:
                num = num + 1
            if num >= 2:
                self.instatus = '4'
                return

        # find 4-4
        for i in range(225):
            num = 0
            if self.d1(i, '1') == 4:
                num = num + 1
            if self.d2(i, '1') == 4:
                num = num + 1
            if self.d3(i, '1') == 4:
                num = num + 1
            if self.d4(i, '1') == 4:
                num = num + 1
            if num >= 2:
                self.instatus = '4'
                return

        return

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
            if self.side == 1:  # invalid move
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
            self.reward = +10
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
                fre = open("result_w.txt", "a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f draw' % (
                self.gamenum, self.posnum, self.winnum, winrate))
                fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f draw' % (
                self.gamenum, self.posnum, self.winnum, winrate)
                fre.close()
            if self.winflag == 1:
                fre = open("result_w.txt","a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f win' %(self.gamenum,self.posnum,self.winnum,winrate))
                fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f win' %(self.gamenum,self.posnum,self.winnum,winrate)
                fre.close()
                # self.saveResult()
            if self.winflag == -1:
                # fre = open("result_w.txt","a")
                winrate = float(self.winnum) / float(self.gamenum) * 100.0
                # fre.write('gamenum : %d, posnum : %d, winnum : %d, rate : %f lose' % (self.gamenum,self.posnum,self.winnum,winrate))
                # fre.write('\n')
                print 'gamenum : %d, posnum : %d, winnum : %d, rate : %f lose' % (self.gamenum,self.posnum,self.winnum,winrate)
                # fre.close()

    def newGame(self):
        self.posnum = 0
        self.reward = 0
        self.lastAction = None
        self.lastState = None
        self.hist = None
        self.hist = []
        self.plate = None
        self.plate = []

        for i in range(225):
            self.plate.append('2')

    def learn(self):
        for i in self.hist:
            tu = i
            if tu[3] == 200 or tu[3] == -300:  # win or lose
                self.ai.learn(tu[0], tu[1], tu[3], tu[2])
            elif tu[3] == 10:  # draw
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
            b = self.plate[i],
            if self.plate[i] == '1': # black -> positive
                c = i,
            elif self.plate[i] == '0': # white -> negative
                c = -i,

            self.inputT = self.inputT + b
            self.dict_input = self.dict_input + c

        state = self.inputT
        dict_state = self.dict_input
        reward = self.reward
        # how to set action init?
        if self.winflag == 2:
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
        self.plate[action] = '0'
        self.posnum += 1

    def saveResult(self):
        f1 = open("win_white.txt", "a")
        for i in range(self.height):
            for j in range(self.width):
                f1.write(self.plate[i * self.width + j])
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

        fr.close()
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
            if i == len(action_list) - 1:  # last learn if white
                if last_Action is not None:
                        temp_tu = (last_State, last_Action, self.dict_input, reward)
                        hist_order.append(temp_tu)
                        # self.ai.learn(last_State, last_Action, reward, self.dict_input) // set last turn result

                if result == 2:
                    if self.side == 1:  # AI Win
                        reward = 200
                    else:
                        reward = -300

                if result == 3:
                    if self.side == 0:  # AI Win
                        reward = 200
                    else:
                        reward = -300

                if result == 4:
                    if self.side == 1:
                        reward = -300

                if result == 5:  # draw
                    reward = 10

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

                if len(action_list)%2 == 0:
                    temp_tu = (last_State, last_Action, self.dict_input, reward)
                    hist_order.append(temp_tu)
                    # self.ai.learn(last_State, last_Action, reward, self.dict_input) // set last turn result

            elif i%2 == 0:  # black move
                temp_state[int(action_list[i])] = 1  # set black move
                self.dict_input = ()
                for j in range(self.height * self.width):
                    c = ()
                    if temp_state[j] == 1:  # black -> positive
                        c = j,
                    elif temp_state[j] == 0:  # white -> negative
                        c = -j,
                    self.dict_input = self.dict_input + c

            elif i%2 == 1: # white move

                if last_Action is not None:
                    temp_tu = (last_State, last_Action, self.dict_input, reward)
                    hist_order.append(temp_tu)
                    # self.ai.learn(last_State, last_Action, reward, self.dict_input)

                last_Action = int(action_list[i])
                self.dict_input = ()
                for j in range(self.height * self.width):
                    c = ()
                    if temp_state[j] == 1:  # black -> positive
                        c = j,
                    elif temp_state[j] == 0:  # white -> negative
                        c = -j,
                    self.dict_input = self.dict_input + c

                last_State = self.dict_input
                temp_state[int(action_list[i])] = 0  # set white move

        for i in hist_order:
            tu = i
            if tu[3] == 200:
                self.ai.learn(tu[0], tu[1], tu[3], tu[2])
            elif result == 2: # black win
                self.ai.learn(tu[0], tu[1], -1, tu[2])
            elif result == 3:  # white win
                self.ai.learn(tu[0], tu[1], 1, tu[2])
            else: # draw
                self.ai.learn(tu[0], tu[1], 0.5, tu[2])

def main():
    agent = Agent(side=0, width=15, height=15)
    agent.newGame()

    # agent.priorInfo()
    # agent.newGame()
    # agent.ai.printQ()

    try:
        while True:
            agent.winflag = 0
            agent.readPlate()
            # agent.printPlate()
            agent.update()
            # agent.printPlate()
            agent.writePlate()
            if agent.instatus != '1':
                # agent.learn()
                agent.getresult()
                agent.newGame()
                # if agent.gamenum > 1000000:
                #     if agent.gamenum % 1000000 == 0:
                #         agent.ai.saveQ()

            if agent.gamenum > 1000000:
                print 'final (gamenum,winrate) : (%d,%f)' %(agent.gamenum, (float(agent.winnum) / float(agent.gamenum) * 100))
                # agent.ai.saveQ()
                break

    except KeyboardInterrupt:
        print 'except --------- '
        # agent.ai.saveQ()


if __name__ == "__main__":
    main()
