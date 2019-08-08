import os
import sys
import glob
import random
import argparse
import numpy as np
import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ROOT = os.path.dirname(os.path.abspath(__file__))
getCachedPics = lambda x : glob.glob(os.path.join(ROOT, 'cropped/proccesed_img50/' + x + '*'))

class App:
    def __init__(self, window,
                       totalTrials = 10,
                       trialPresentation = 'single300',
                       categoryType = 'fruit',
                       baseItem = 'apple'):

        '''
        Sets up logic for running the task.
        '''
        self.correct = 0
        self.currentTrial = 0
        self.totalTrials = totalTrials
        self.trialPresentation = trialPresentation
        self.categoryType = categoryType
        self.baseItem = baseItem

        #alllowed categories and items within categories
        self.Cats = {'fruit' : ['apple','grape','banana','pineapple'],
                     'fruitsVegNoConflict' : ['apple','grape',
                                              'banana','pineapple',
                                              'broccoli','carrot',
                                              'corn','mushrooms'],
                     'fruitsVegConflict' : ['apple','grape','banana',
                                            'pineapple','broccoli',
                                            'carrot','corn','mushrooms',
                                            'potato','onion'],
                    'gestures' : ['thumbs_up', 'thumbs_down', 'OK_sign',
                                  'peace_sign', 'stop_sign']}

        '''
        Argument checker -> fall within expected ranges or exits
        '''
        if self.totalTrials <= 0 or self.totalTrials > 40:
            print('Number of trials not in acceptable range, EXITING')
            sys.exit(0)
        if self.categoryType not in self.Cats.keys():
            print('categoryType entered not valid, EXITING')
            print('catgories that are allowed:')
            print('\tfruit')
            print('\tfruitsVegNoConflict')
            print('\tfruitsVegConflict')
            print('\tgestures')
            sys.exit(0)
        else:
            for element in self.Cats[self.categoryType]:
                items = getCachedPics(element)
                if len(items) == 0:
                    print('Element %s has no pictures, EXITING' %element)
                    sys.exit(0)
                else:
                    print("We have %i pictures of %s" %(len(items), element))

        if self.trialPresentation not in ['continuous','single300','triple300']:
            print('trialPresentation entered not valid, EXITING')
            print('Allowed modes are:')
            print('\tcontinuous')
            print('\tsingle300')
            print('\ttriple300')
            sys.exit(0)
        if self.baseItem not in self.Cats[self.categoryType]:
            print('base item entered should be in the category, EXITING')
            print('you specified %s as base item' %self.baseItem)
            print('Items in current category are:')
            for s in self.Cats[self.categoryType]:
                print('\t%s' %s)
            sys.exit(0)

        '''
        Generates trials in advanced. Half of the trials are of the target base
        item, the other half of any of the other items within that category. The
        order of the trials is then randomly shuffled
        '''
        alternatives = [w for w in self.Cats[categoryType] if w != self.baseItem]
        self.trialTypes = [self.baseItem if w%2==0 \
                                         else random.choice(alternatives)
                                         for w in range(self.totalTrials)]
        random.shuffle(self.trialTypes)

        '''
        GUI parameters. Sets up window, buttons, canvas, and message box.
        '''
        self.window = window
        self.window.title("Fruit Recognition")
        self.window.geometry('1200x1000')
        self.frame = tk.Frame(window)

        self.button_Yes = tk.Button(self.frame, text="YES", height = 10, width = 20, command=self.yes_decision)
        self.button_Yes.pack(side="left")
        self.button_No = tk.Button(self.frame, text="NO", height = 10, width = 20, command=self.no_decision)
        self.button_No.pack(side="right")

        self.label = tk.Label(self.window,
                              text="Is there a %s in this picture?" %self.baseItem,
                              font=("Arial Bold", 50)).pack()

        my_dpi = 192
        fig, ax = plt.subplots(1,1,figsize=(50/my_dpi, 50/my_dpi), dpi=my_dpi)
        self.pic = ax.imshow(np.zeros((50,50)), cmap=plt.get_cmap('gray'), vmin=0, vmax=1)
        self.canvas = FigureCanvasTkAgg(fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.frame.pack()

        #START SESSION!
        self.window.after(1000, self.next_trial)


    def load_image(self, img_path):
        return mpimg.imread(img_path)

    def get_picture_cached(self, fruit, notAllowed = []):
        '''
        It picks a picture at random of the given category, if it has not been
        shown before. If there are a lot of trials it could get stuck in an
        infinite loop because all pictures have been shown. That's why it will
        only look 50 times, and quit the program if it exceeds that.
        '''
        cnt = 0
        specificPic = random.choice(getCachedPics(fruit))
        while specificPic in notAllowed and cnt < 50:
            specificPic = random.choice(getCachedPics(fruit))
            cnt += 1
        notAllowed.append(specificPic)
        #we print the picture in case it's not good, it gives us the name in the
        #terminal and that way we can manually delete it.
        print(specificPic)
        return self.load_image(specificPic)

    def draw_array(self, img):
        self.pic.set_data(img)
        self.canvas.draw()

    def display_stimulus(self):
        self.draw_array(self.get_picture_cached(self.trialTypes[self.currentTrial]))

    def blank_screen(self):
        self.draw_array(np.zeros((50,50)))

    def yes_decision(self):
        self.correct += (self.trialTypes[self.currentTrial] == self.baseItem)
        self.currentTrial += 1
        self.next_trial()

    def no_decision(self):
        self.correct += (self.trialTypes[self.currentTrial] != self.baseItem)
        self.currentTrial += 1
        self.next_trial()


    def next_trial(self):
        if self.currentTrial < self.totalTrials:
            if self.trialPresentation == 'continuous':
                self.display_stimulus()
            elif self.trialPresentation == 'single300':
                self.window.after(100, self.display_stimulus)
                self.window.after(300, self.blank_screen)
            elif self.trialPresentation == 'triple300':
                im = self.get_picture_cached(self.trialTypes[self.currentTrial])
                for _ in range(3):
                    self.draw_array(im)
                    self.frame.after(300)
                    self.blank_screen()
                    self.frame.after(100)

        else:
            print('*'*80)
            print('Total Score: %i/%i' %(self.correct, self.totalTrials))
            print('*'*80)
            self.window.quit()



if __name__ == '__main__':
    print('''
    This GUI draws pictures from ./cropped/proccesed_img50/.
    If there are no pictures there, the program will not work!
    Images should be processed to be grayscale and 50x50.
    ''')
    if not os.listdir(os.path.join(ROOT, 'cropped/proccesed_img50')):
        print('There are no pictures in ./cropped/procces   ed_img50')
        sys.exit(0)

    #command line argument parser
    parser = argparse.ArgumentParser(description='Image Recognition for Humans.')
    parser.add_argument('--trials', type=int, default = 10,
                        help="The number of trials to run.")
    parser.add_argument('--trialPresentation', type=str, default = 'single300',
                        help = 'How to present each stimuli.')
    parser.add_argument('--categoryType', type=str, default = 'fruit',
                        help = 'Present fruits, fruits and vegetables, etc.')
    parser.add_argument('--baseItem', type=str, default = 'apple',
                        help = 'The base category to compare against')
    args = parser.parse_args()


    root = tk.Tk()
    app = App(root, totalTrials = args.trials,
                    trialPresentation = args.trialPresentation,
                    categoryType = args.categoryType,
                    baseItem = args.baseItem)
    root.mainloop()
