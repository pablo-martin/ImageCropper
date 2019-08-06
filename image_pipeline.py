import os
import sys
import glob
import argparse
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from skimage.transform import rescale
from ImageCropper import ImageCropper

ROOT = os.path.dirname(os.path.abspath(__file__))

def load_image(img_path):
    return mpimg.imread(img_path)

def convert_to_png(folder):
    for image_file in glob.glob(folder + '/*jpg'):
        im = Image.open(image_file)
        im.save(image_file[:-3] + 'png')
        os.remove(image_file)
    return

def rgb2gray(img):
    return np.dot(img[:,:,:3], [0.2989, 0.5870, 0.1140])

def downsample_image(img, pixelWidth = 50):
    img = img[:min(img.shape), :min(img.shape)]
    return rescale(img, pixelWidth / img.shape[0], anti_aliasing=False, multichannel=False)

def add_dark_padding(specificPic, outputDir = 'cropped/proccesed_imgPad/'):
    img = load_image(specificPic)
    new_img = np.zeros((120,120))
    new_img[35:85,35:85] = img[:,:,0]
    plt.imsave(outputDir + os.path.basename(specificPic), new_img, cmap=plt.get_cmap('gray'))
    return

def create_50x50(inputDir, pixelWidth = 50):
    for image_file in glob.glob(inputDir + '/*png'):
        im = load_image(image_file)
        im = rgb2gray(im)
        im = downsample_image(im, pixelWidth = pixelWidth)
        plt.imsave(image_file, im, cmap=plt.get_cmap('gray'))
        print('Finished processing %s.' %(os.path.basename(image_file)))
    return

def create_120x120_darkpad(inputDir, outputDir = ROOT + '/cropped/proccesed_imgPad/'):
    assert(os.path.isdir(outputDir))
    for image_file in glob.glob(inputDir + '/*png'):
        add_dark_padding(image_file, outputDir = outputDir)
        print('Adding dark padding to %s.' %(os.path.basename(image_file)))
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pablo Image Pipeline.')
    parser.add_argument('--inputDir', type=str, default = '.',
                        help="Directory where input images are.")
    parser.add_argument('--inputPrefix', type=str, default = '',
                        help = 'Prefix to select all images containing this keyword.')
    parser.add_argument('--outputDir', type=str, default = './cropped',
                        help = 'Directory where output images are saved to.')
    parser.add_argument('--outputPrefix', type=str, default = '',
                        help = 'Prefix to use for output files.')
    parser.add_argument('--resolution', type=int, default = 300,
                        help = 'DPI resolution of output images.')
    parser.add_argument('--extension', type=str, default = 'png',
                        help = 'Extension for output images, must be png or jpg.')
    parser.add_argument('--imgPadDir', type=str, default = 'cropped/proccesed_imgPad/',
                        help = 'Directory where processed padded images should go.')
    parser.add_argument('--offset', type=int, default = 100,
                        help = 'How many pixels we want the image to move during cropping.')
    parser.add_argument('--pixelWidth', type=int, default = 50,
                        help = 'Resolution of output image, default is 50x50')
    parser.add_argument('--addDarkPad', type=str, default = 'No',
                        help = 'Should be "Yes" if we want to add dark padding.')
    args = parser.parse_args()

    if not os.path.isdir(args.inputDir):
        print("Input directory not valid! EXITING")
        sys.exit(0)
    if not os.path.isdir(args.outputDir):
        print("Output directory not valid! EXITING")
        sys.exit(0)
    if not args.outputPrefix:
        print("You must specify output prefix! EXITING")
        sys.exit(0)
    if args.extension not in ['jpg','png']:
        print('Extension must be png or jpg only! EXITING')
        sys.exit(0)
    if not os.path.isdir(args.imgPadDir):
        print("Directory for padded images not valid! EXITING")
        sys.exit(0)


    print('''
Use the left ard right arrows to change image.

Click and drag a box to crop.

Close window to exit.

    ''')
    input('\npress Enter to begin')

    IC = ImageCropper(infile_folder = args.inputDir,
                      infile_prefix = args.inputPrefix,
                      outfile_folder = args.outputDir,
                      outfile_prefix = args.outputPrefix,
                      outfile_extension = args.extension,
                      offset = args.offset,
                      resolution = args.resolution)
    #Run cropping tool
    IC.mainloop()
    #convert output of cropping to png in case it's not converted
    convert_to_png(args.outputDir)
    #turning to gray scale and downsampling to 50 by 50
    create_50x50(args.outputDir, pixelWidth = args.pixelWidth)
    #adding dark padding for use in neural code setup
    if args.addDarkPad == 'Yes':
        create_120x120_darkpad(args.outputDir, outputDir = os.path.join(ROOT, args.imgPadDir))
