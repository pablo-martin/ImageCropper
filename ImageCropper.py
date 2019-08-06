import os
import glob
import pygame, sys
from pygame.locals import K_a, K_s, K_w, K_d, K_LEFTBRACKET, K_RIGHTBRACKET, K_RIGHT, K_LEFT, QUIT
from PIL import Image

class ImageCropper():
    def __init__(self, infile_folder = '.',
                       infile_prefix = '',
                       outfile_folder = './cropped',
                       outfile_prefix = '',
                       outfile_extension = 'png',
                       offset = 100,
                       resolution = 300):

        #general properties
        self.topleft = None
        self.bottomright = None
        self.prior = None
        self.scale = 1
        self.pos = [0,0]
        self.BG_COLOR = (0,0,0)
        self.offset = offset
        self.resolution = resolution

        #Getting input images appropriately
        self.infile_folder = infile_folder
        self.infile_prefix = infile_prefix
        #create list of files matching prefix in folder, and sort it
        self.infiles = [os.path.basename(w) \
                   for w in glob.glob(os.path.join(infile_folder, infile_prefix) + '*.png')]
        self.infiles.sort()
        if not self.infiles:
            print("No files found in input folder with that input prefix!")
            return
        else:
            print("We found %i files: \n" %len(self.infiles))
        self.file_idx = 0
        self.input_loc = os.path.join(self.infile_folder, self.infiles[self.file_idx])


        #get files begining with output prefix to make sure we don't overwrite files
        self.outfile_folder = outfile_folder
        self.outfile_prefix = outfile_prefix
        self.outfile_extension = outfile_extension

        outfiles = [w for w in glob.glob(os.path.join(outfile_folder, outfile_prefix) + '*') \
                    if os.path.isfile(w)]
        outfiles.sort()
        self.out_idx = len(outfiles)

        self.outfilename = lambda x : self.outfile_prefix + str(x).zfill(3) + '.' + self.outfile_extension
        self.output_loc = os.path.join(outfile_folder, self.outfilename(self.out_idx))

        #initialize graphics window / render it
        self.px = pygame.image.load(self.input_loc)
        self.screen = pygame.display.set_mode([self.px.get_rect().width,\
                                               self.px.get_rect().height])
        self.screen.blit(self.px, self.px.get_rect())
        pygame.display.flip()


    def move(self):
        '''
        Moves image by self.pos
        '''
        x,y = self.pos
        rect = self.px.get_rect()
        self.screen.fill(self.BG_COLOR)
        self.px = pygame.transform.scale(self.px, [int(rect.width/self.scale),\
                                                   int(rect.height/self.scale)])
        self.screen.blit(self.px, (rect[0] - x, rect[1] - y))
        pygame.display.flip()
        return

    def displayRect(self):
        '''
        Draws gray rectangle so user knows what you're intending to crop
        '''
        if self.topleft == None:
            #func was called without a topleft, which means clear the previous rectangle
            self.screen.fill(self.BG_COLOR)
            rect = self.px.get_rect()
            self.px = pygame.transform.scale(self.px, [int(rect.width/self.scale),\
                                                       int(rect.height/self.scale)])
            self.screen.blit(self.px, (rect[0] - self.pos[0], rect[1] - self.pos[1]))
            pygame.display.flip()
            return None

        #or, the usual situation, topleft is defined, so blit over the old rect and blit in the new.
        self.topleft = [(val/self.scale - self.pos[i]) for i, val in enumerate(self.topleft)]
        x, y = self.topleft
        bottomright = pygame.mouse.get_pos()
        width =  bottomright[0] - self.topleft[0]
        height = bottomright[1] - self.topleft[1]
        if width < 0:
            x += width
            width = abs(width)
        if height < 0:
            y += height
            height = abs(height)

        # eliminate redundant drawing cycles (when mouse isn't moving)
        current = x, y, width, height
        if not (width and height):
            return current
        if current == self.prior:
            return current

        # draw transparent box and blit it onto canvas
        rect = self.px.get_rect()
        self.px = pygame.transform.scale(self.px, [int(rect.width/self.scale),
                                                   int(rect.height/self.scale)])
        self.screen.blit(self.px, (rect[0] - self.pos[0],rect[1] - self.pos[1]))
        #draw gray rectangle
        im = pygame.Surface((width, height))
        im.fill((128, 128, 128))
        pygame.draw.rect(im, (32, 32, 32), im.get_rect(), 1)
        im.set_alpha(128)
        self.screen.blit(im, (x, y))
        pygame.display.flip()
        # return current box extents
        return (x, y, width, height)


    def mainloop(self):
        pygame.init()
        runForever = 1
        while runForever:
            for event in pygame.event.get():

                if event.type == QUIT:
                    runForever = 0
                    pygame.display.quit()
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.topleft == None:
                        self.topleft = [(val+self.pos[i]) * self.scale for i, val in enumerate(event.pos)]
                    else:
                        self.bottomright = [(val+self.pos[i]) * self.scale for i, val in enumerate(event.pos)]


                if event.type == pygame.KEYDOWN and event.key == K_a:
                    self.pos = [self.pos[0] - self.offset, self.pos[1]]
                    self.move()
                if event.type == pygame.KEYDOWN and event.key == K_d:
                    self.pos = [self.pos[0] + self.offset, self.pos[1]]
                    self.move()
                if event.type == pygame.KEYDOWN and event.key == K_w:
                    self.pos = [self.pos[0], self.pos[1] - self.offset]
                    self.move()
                if event.type == pygame.KEYDOWN and event.key == K_s:
                    self.pos = [self.pos[0], self.pos[1] + self.offset]
                    self.move()


                if event.type == pygame.KEYDOWN and event.key == K_RIGHTBRACKET:
                    self.scale /= 1.25
                    self.move()
                if event.type == pygame.KEYDOWN and event.key == K_LEFTBRACKET:
                    self.scale *= 1.25
                    self.move()

                if event.type == pygame.KEYDOWN and event.key == K_RIGHT:
                    self.file_idx += 1
                    try:
                        infile = self.infiles[self.file_idx]
                    except IndexError:
                        self.file_idx -= 1
                        print("End of album")
                    else:
                        self.input_loc = os.path.join(self.infile_folder, infile)
                        self.px = pygame.image.load(self.input_loc)
                        pos = [0,0]
                        self.topleft = self.bottomright = self.prior = None
                        self.prior = self.displayRect()

                if event.type == pygame.KEYDOWN and event.key == K_LEFT:
                    if self.file_idx == 0:
                        print("This is the begining of the album, cannot go back a page.")
                    else:
                        self.file_idx -= 1
                        infile = self.infiles[self.file_idx]
                        self.input_loc = os.path.join(self.infile_folder,infile)
                        self.px = pygame.image.load(self.input_loc)
                        pos = [0,0]
                        self.topleft = self.bottomright = self.prior = None
                        self.prior = self.displayRect()


            if self.topleft:
                #first corner has been selected
                self.prior = self.displayRect()
                if self.bottomright:
                    #selection has been made!

                    left, upper, right, lower = ( self.topleft + self.bottomright )
                    # ensure output rect always has positive width, height
                    if right < left:
                        left, right = right, left
                    if lower < upper:
                        lower, upper = upper, lower

                    #actual cropping happens here
                    im = Image.open(self.input_loc)
                    im = im.crop((int(left), int(upper), int(right), int(lower)))
                    #if coordinates were valid we save the image
                    if im.getbbox() != None:
                        im.save(self.output_loc, dpi = (self.resolution, self.resolution))
                        self.out_idx += 1
                        self.output_loc = os.path.join(self.outfile_folder, self.outfilename(self.out_idx))
                        self.topleft = self.bottomright = self.prior = None
                        self.prior = self.displayRect()
                        print("saved")
                    else:
                        self.topleft = self.bottomright = self.prior = None
                        print("Not valid mouse selection")

        return


if __name__ == '__main__':
    '''
    For debugging purposes only.
    '''
    IC = ImageCropper(infile_folder = 'pics/my_pics/apples/',
                       infile_prefix = 'apple',
                       outfile_folder = './cropped/test/',
                       outfile_prefix = 'appletest',
                       outfile_extension = 'png',
                       offset = 100,
                       resolution = 300)

    IC.mainloop()
