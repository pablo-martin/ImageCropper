 # Pablo Image Pipeline  

Small package to do two things:  
1) Crop and downsample images  
2) Play a game to guess which image is flashed at you  

---
(1) Image Cropper
 Main script is image_pipeline.py. In general, you can point it to a folder with
 pictures in jpg or png format, then a window will pop up allowing you to crop
 subsections of the images. Use left or right arrow to move through your pictures,
 and click and drag box across image to select section to crop, then click to
 save image.  

 Tool runs on the command line, clone repo into some directory, navigate to it
 using the terminal and type  
```console
macbook:ImageCropper pablo$ python image_pipeline.py --help
```

This should give you a description of the options you need to provide the tool.  
---  
(2) Image GUI  
In general, this tool is less flexible than the cropper. You need to create a
folder inside the package called './cropped/proccesed_img50/', and all the
pictures should be there, and should be processed appropriately. They should
start with the name specified in the categories, and they should be 50x50 pixels,
grayscale and png.  

Similarly, you can type the following to get more information:  
```console
macbook:ImageCropper pablo$ python FRUIT_GUI.py --help
```
