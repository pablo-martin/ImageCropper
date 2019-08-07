import os
import sys
import glob
import argparse
from shutil import copyfile, rmtree
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from skimage.transform import rescale
from ImageCropper import ImageCropper

ROOT = os.path.dirname(os.path.abspath(__file__))

'''
We like working with png so we convert every jpg and then delete original jpg
'''
def convert_jpg_to_png(folder, outputDir = os.path.join(ROOT, 'tmp'), deleteOriginal=False):
    for image_file in os.listdir(folder):

        if image_file[-3:] == 'jpg':
            im = Image.open(os.path.join(folder, image_file ))
            im.save(os.path.join(outputDir, image_file[:-3] + 'png'))
            if deleteOriginal: os.remove(image_file)
        elif image_file[-3:] == 'png':
            copyfile(os.path.join(folder, image_file), os.path.join(outputDir, image_file))
        else:
            print("%s is not a valid picture, skipping." %image_file)
    return


def rename_pics(dire, substr, extension):
    for i,image_file in enumerate(os.listdir(dire)):
        os.rename(os.path.join(dire, image_file), os.path.join(dire, substr + str(i) + extension))

'''
Functions to turn image to grayscale and downsample
'''
def load_image(img_path):
    return mpimg.imread(img_path)

def rgb2gray(img):
    return np.dot(img[:,:,:3], [0.2989, 0.5870, 0.1140])

def downsample_image(img, pixelWidth = 50):
    img = img[:min(img.shape), :min(img.shape)]
    return rescale(img, pixelWidth / img.shape[0], anti_aliasing=False, multichannel=False)

def create_50x50(inputDir, pixelWidth = 50):
    for image_file in glob.glob(inputDir + '/*png'):
        im = load_image(image_file)
        im = rgb2gray(im)
        im = downsample_image(im, pixelWidth = pixelWidth)
        plt.imsave(image_file, im, cmap=plt.get_cmap('gray'))
        print('Finished processing %s.' %(os.path.basename(image_file)))
    return


'''
Functions to add dark padding to make 120x120. Only works with pictures that are
50x50
'''

def add_dark_padding(specificPic, outputDir = 'cropped/proccesed_imgPad/'):
    img = load_image(specificPic)
    new_img = np.zeros((120,120))
    if (img.shape[0] == 50 and img.shape[1] == 50):
        new_img[35:85,35:85] = img[:,:,0]
        plt.imsave(outputDir + os.path.basename(specificPic), new_img, cmap=plt.get_cmap('gray'))
        return
    else:
        print("input image is not 50x50. Did not convert.")
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
    parser.add_argument('--pixelWidth', type=int, default = 50,
                        help = 'Resolution of output image, default is 50x50')
    parser.add_argument('--addDarkPad', type=str, default = 'No',
                        help = 'Should be "Yes" if we want to add dark padding.')
    args = parser.parse_args()

    if not os.path.isdir(args.inputDir) or not os.listdir(args.inputDir):
        print("Input directory not valid or empty! EXITING")
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


    tmp_dir = os.path.join(ROOT, 'tmp')
    if os.path.isdir(tmp_dir):
        rmtree(tmp_dir)
    os.mkdir(tmp_dir)


    #convert input pictures from jpg to png and save to tmp folder
    convert_jpg_to_png(args.inputDir, outputDir = tmp_dir, deleteOriginal=False)

    #Instructions for cropping
    print('''
            Use the left ard right arrows to change image.

            Click and drag a box to crop.

            Close window to exit.''')

    input('\npress Enter to begin')

    #define cropper
    IC = ImageCropper(infile_folder = tmp_dir,
                      infile_prefix = args.inputPrefix,
                      outfile_folder = args.outputDir,
                      outfile_prefix = args.outputPrefix,
                      outfile_extension = args.extension,
                      resolution = args.resolution)
    #Run cropping tool
    IC.mainloop()

    #convert output of cropping to png in case it's not converted
    convert_jpg_to_png(args.outputDir)

    #turning to gray scale and downsampling to 50 by 50
    create_50x50(args.outputDir, pixelWidth = args.pixelWidth)

    #adding dark padding for use in neural code setup
    if args.addDarkPad == 'Yes':
        create_120x120_darkpad(args.outputDir, outputDir = os.path.join(ROOT, args.imgPadDir))

    #delete tmp dir
    rmtree(tmp_dir)
