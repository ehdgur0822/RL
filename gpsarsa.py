# -*- coding: utf-8 -*-
"""
copyright Kwangho Heo
2016-07-04
"""
import numpy as np
from math import *
import util
import pickle
from numpy import random


class GPTDController:

    steps = 0
    _epsilon = 0.1
    # Meta parameters
    nu = 7
    sigma0 = 10.0
    gamma = 0.9

    # Gaussian Kernel parameters
    kernel_sigma = 0.5
    kernel_p = 2.0

    # Linear Kernel parameters
    lkernel_p = 1
    lkernel_sigma = 0

    tmp_action_values = []  # just for print

    def __init__(self, initial_state, initial_action, fixed_epsilon=True):

        self.fixed_epsilon = fixed_epsilon
        self.width = 7
        self.height = 7
        self.actions = range(self.height * self.width)

        try:
            with open('gpvalue.txt', 'r') as f:
                (self.C, self.c, self.alpha, self.d, self.sinv, self.Kinv, self.a, self.dict) = pickle.load(f)

        except IOError:
            self.C = util.GrowingMat((0, 1), (100, 100))
            self.c = util.GrowingVector(0)
            self.alpha = util.GrowingVector(0)
            self.d = 0
            self.sinv = 0
            self.Kinv = util.GrowingMat((0, 1), (100, 100))
            self.actions = range(self.height * self.width)

            # array of tuples: [(b0, a0), (b1, a1), (s2, a2)]
            self.dict = [(initial_state, initial_action)]
            self.Kinv.expand(rows=np.array([[1. / self.fullKernel_pair(initial_state, initial_action)]]))
            self.C.expand(rows=np.array(0))
            self.a = np.array(1)
            self.c.expand(rows=np.array(0))
            self.alpha.expand(rows=np.array(0))
            pass

    def set_epsilon(self, epsilon):
        self._epsilon = epsilon

    def get_best_action(self, state):
        self.validactions = []
        self.min_x = self.width - 1
        self.max_x = 0
        self.min_y = self.height - 1
        self.max_y = 0
        self.temp_x = 0
        self.temp_y = 0
        for a in self.actions:
            if state[a] == 1 or state[a] == 0:
                # self.validactions.append(a)
                self.temp_x = a % self.width
                self.temp_y = (a - self.temp_x) / self.height
                # print 'temp %d %d' % (self.temp_x, self.temp_y)
                if self.temp_x < self.min_x:
                    self.min_x = self.temp_x
                if self.temp_x > self.max_x:
                    self.max_x = self.temp_x
                if self.temp_y < self.min_y:
                    self.min_y = self.temp_y
                if self.temp_y > self.max_y:
                    self.max_y = self.temp_y

        # print '1: %d %d %d %d' % (self.min_x, self.max_x, self.min_y, self.max_y)

        if self.min_x - 3 < 0:
            self.min_x = 0
        else:
            self.min_x -= 3

        if self.max_x + 3 > self.width-1:
            self.max_x = self.width-1
        else:
            self.max_x += 3

        if self.min_y - 3 < 0:
            self.min_y = 0
        else:
            self.min_y -= 3

        if self.max_y + 3 > self.height-1:
            self.max_y = self.height-1
        else:
            self.max_y += 3

        #print '2: %d %d %d %d' %(self.min_x, self.max_x, self.min_y, self.max_y)

        for i in range(self.min_y, self.max_y+1):
            for j in range(self.min_x, self.max_x+1):
                a = self.width * i + j
                if state[a] == 2:
                    self.validactions.append(a)

        if np.random.sample() <= self.epsilon(self.steps):
            # epsilon-greedy with 0.1 taking random action
            best = np.random.choice(self.validactions)
            # print '<<<epsilon random action...>>>'
        else:
            values = {}
            for action in self.validactions:
                kvec = self.getKVector(state, action)      # size: m
                values[action] = float(np.inner(kvec.T, self.alpha.view.flatten()))
            pass
            # print 'values: %s' % [float(np.round(v, 4)) for v in values]
            v = np.amax(values.values())
            bests = []
            for action in self.validactions:
                if values[action] == v:
                    bests.append(action)
            best = np.random.choice(bests)
            self.tmp_action_values = values
        # best = self.get_random_action()
        return best

    def observe_step(self, old_state, old_action, reward, new_state, new_action):
        self.steps += 1
        print 'old_state: %s' % np.round(old_state.flatten(), 3)
        print 'old_action: %s' % self.actions[old_action]
        print 'new_state: %s' % np.round(new_state.flatten(), 3)
        print 'new_action: %s' % self.actions[new_action]
        k = self.getKVector(new_state, new_action)

        a = np.array(np.dot(self.Kinv.view, k)).flatten()
        ktt = float(self.fullKernel_pair(new_state, new_action))
        dk = self.getKVector(old_state, old_action) - self.gamma * self.getKVector(new_state, new_action)
        delta = ktt - float(np.inner(k.T, a))
        self.d = self.d * self.sinv * self.gamma * self.sigma0 ** 2 + \
            reward - float(np.inner(dk, self.alpha.view.flatten()))

        print 'delta: %f' % delta
        print 'dictionary size: %d' % len(self.dict)
        # sparsification test
        if delta > self.nu:
            dk2 = np.array((self.getKVector(old_state, old_action) - 2 *
                            self.gamma * self.getKVector(new_state, new_action))).flatten()
            self.dict.append((new_state, new_action))
            # update K^-1
            self.Kinv.view = delta * self.Kinv.view + np.outer(a, a)
            self.Kinv.expand(cols=-a.reshape(-1, 1),
                             rows=-a.reshape(1, -1),
                             block=np.array([[1]])
                             )
            self.Kinv.view /= delta
            # print "inverted Kernel matrix:", self.Kinv.view

            a = np.zeros(self.Kinv.shape[0])
            a[-1] = 1

            hbar = np.zeros_like(a)
            hbar[:-1] = self.a
            hbar[-1] = - self.gamma

            dktt = float(np.inner(self.a, dk2)) + self.gamma ** 2 * ktt

            cm1 = self.c.view.copy().flatten()
            self.c.view = self.c.view.flatten() * self.sinv * self.gamma * self.sigma0 ** 2 \
                + self.a - np.dot(self.C.view, dk)
            self.c.expand(rows=np.array(- self.gamma))

            s = (1 + self.gamma ** 2) * self.sigma0 ** 2 - self.sinv * self.gamma ** 2 * self.sigma0 ** 4 + dktt \
                - np.dot(dk, np.dot(self.C.view, dk)) + 2 * self.sinv * self.gamma * self.sigma0 ** 2 * np.dot(cm1, dk)

            self.alpha.expand(rows=np.array([[0]]))
            self.C.expand(rows=np.zeros((1, self.C.shape[1])),
                          cols=np.zeros((self.C.shape[0], 1)))
            pass

        else:
            self.hbar = self.a - self.gamma * a
            cm1 = self.c.view.copy()
            self.c.view = self.c.view.flatten() * self.sinv * self.gamma * self.sigma0 ** 2 + self.hbar \
                - np.dot(self.C.view, dk)

            s = (1 + self.gamma ** 2) * self.sigma0 ** 2 - self.sinv * self.gamma ** 2 * self.sigma0 ** 4 + \
                np.dot(dk, self.c.view + self.gamma * self.sigma0 ** 2 * self.sinv * cm1)
            pass

        self.sinv = 1 / s
        self.alpha.view += self.sinv * self.d * self.c.view
        self.C.view += self.sinv * np.outer(self.c.view, self.c.view)
        self.a = a
        pass

    def getKVector(self, new_state, new_action):
        k = np.zeros(len(self.dict))
        for i in range(len(k)):
            k[i] = self.fullKernel(self.dict[i][0], new_state,
                                   self.dict[i][1], new_action)
        return k

    def fullKernel_pair(self, state, action):
        return self.stateKernel_pair(state) + self.actionKernel_pair(action)

    def fullKernel(self, s1, s2, a1, a2):
        return self.stateKernel(s1, s2) + self.actionKernel(a1, a2)

    def stateKernel_pair(self, state):
        return self.stateKernel(state, state)

    def stateKernel(self, s1, s2):
        """
        Kernel of two state vector s1, s2, return value will be a scala
        """
        # Gaussian kernel with param (sigma=5, p=4)
        v = - (np.linalg.norm(s1-s2) ** 2) / (2 * self.kernel_sigma ** 2)
        result = pow(self.kernel_p, 2) * exp(v)

        # scaled norm kernel
        # result = 1 - np.linalg.norm(s1-s2) ** 2 / (np.linalg.norm(s1) ** 2 * np.linalg.norm(s2) ** 2)
        return result

    def actionKernel_pair(self, action):
        return self.actionKernel(action, action)

    def actionKernel(self, a1, a2):
        """
        Kernel of two action a1, a2, return value will be a scala
        """
        # for simplicity just using delta-kernel
        # result = 1 if a1 == a2 else 0
        v = - (np.linalg.norm(a1 - a2) ** 2) / (2 * self.kernel_sigma ** 2)
        result = pow(self.kernel_p, 2) * exp(v)
        return result

    def end(self):
        print 'end debug here'
        print 'dictionary length: %d' % len(self.dict)
        print '---------- dictionary -----------'
        for tup in self.dict:
            print '(%s, %s), %s' % (tup[0][0].item(0), tup[0][1].item(0), self.actions[tup[1]])
        # print 'alpha: %s' % self.alpha.view.flatten()

    def saveQ(self):
        with open('gpvalue.txt', 'wb') as f:
            pickle.dump((self.C, self.c, self.alpha, self.d, self.sinv, self.Kinv, self.a, self.dict), f)

    def epsilon(self, steps):
        if self.fixed_epsilon:
            return self._epsilon
        else:
            e = 0.2 / np.log10(steps+10)
            print 'epsilon: %f' % e
            return e
