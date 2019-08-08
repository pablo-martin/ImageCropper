import os
import sys
import glob
import argparse
from shutil import copyfile, rmtree
from PIL import Image
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


'''
Functions to turn image to grayscale and downsample
'''

def create_50x50(inputDir, pixelWidth = 50):
    for image_file in glob.glob(inputDir + '/*png'):
        im = Image.open(image_file)
        #turn to grayscale
        im = im.convert('LA')
        #downsample
        im = im.resize((pixelWidth, pixelWidth))
        #save image
        im.save(image_file)
        print('Finished processing %s.' %(os.path.basename(image_file)))
    return


'''
Functions to add dark padding to make 120x120. Only works with pictures that are
50x50
'''
def create_120x120_darkpad(inputDir, outputDir = ROOT + '/cropped/proccesed_imgPad/'):
    assert(os.path.isdir(outputDir))
    for image_file in glob.glob(inputDir + '/*png'):
        im = Image.open(image_file)
        back = Image.new(size = (120,120), mode='RGB')
        if im.size == (50,50):
            back.paste(im, (35,35))
            back.save(outputDir + os.path.basename(image_file))
            print('Adding dark padding to %s.' %(os.path.basename(image_file)))
        else:
            print("input image %s is not 50x50. Skipping." %(os.path.basename(image_file)))
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
