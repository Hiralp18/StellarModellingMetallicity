from __future__ import division, print_function
from multiprocessing import Process, Lock, Array
from constants import *
from composition import Composition
from rkf import rkf
from bisection import bisection
import matplotlib.pyplot as plt
from matplotlib import rc
from stellar_generator import Star

# Computer modern fonts
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

# Main sequence class
# USAGE :
#       ms = MainSequence(min_core_temp = $some temp$, max_core_temp = $some temp$, X = $some comp$, Y = $some comp$, num_of_stars = $some num$)
#
# INPUT:
#       You know
#
# OUTPUT:
#       Plot !!!


class MainSequence():
    def __init__(self, min_core_temp, max_core_temp,X,Y,num_of_stars):
        self.min_core_temp = min_core_temp
        self.max_core_temp = max_core_temp
        self.num_of_stars = num_of_stars
        self.composition = Composition.fromXY(X,Y)
        self.lumin = [0] * num_of_stars
        self.lock = Lock()
    def make_entry(self,t,l,ind,temp,lumin):
        self.lock.acquire()
        temp[ind] = t
        lumin[ind] = l/L_s
        print("Star {0} : Temp {1} : Lumin {2} ".format(ind, t, l))
        self.lock.release()
    def make_star(self,t,index,temp,lumin):
        star =  Star(temp_c = t, composition=self.composition)
        star.solve()
        star.log_solved_properties()
        self.make_entry(star.temp_surf,star.lumin_surf,index,temp,lumin)
    def calculate(self,temp,lumin):
        core_temp = np.linspace(start=self.min_core_temp,stop=self.max_core_temp,num=self.num_of_stars)
        print(core_temp)
        procs = []
        for idx, t in enumerate(core_temp):
             p = Process(target=self.make_star,args=(t,idx,temp,lumin))
             procs.append(p)
             p.start()
        for p in procs:
            p.join()

    def plot(self):
        ## For synchromization create process safe array
        temp = Array("d",[0]*self.num_of_stars)
        lumin = Array("d",[0]*self.num_of_stars)
        self.calculate(temp,lumin)
        tempArr = temp[:]
        luminArr = lumin[:]
        print (tempArr)
        print (luminArr)
        plt.figure()
        plt.title(r"Main Sequence")
        plt.xlabel(r"Temparature")
        plt.ylabel(r"$L/L_{\odot}$")
        plt.plot(tempArr,luminArr)
        plt.gca().invert_xaxis()
        plt.gca().set_yscale("log")
        plt.gca().set_xscale("log")
        plt.savefig("../figures/main_sequence_{0}_stars.pdf".format(self.num_of_stars), format="pdf")
        plt.show()

if __name__ == "__main__":
    ms = MainSequence(min_core_temp=5e6,max_core_temp=3.5e7,X=0.73,Y=0.25,num_of_stars=20)
    ms.plot()
