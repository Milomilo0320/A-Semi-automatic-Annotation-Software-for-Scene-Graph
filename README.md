<p align="center">
    <img src='teaser_image/logo.png'>
</p>

# A-Semi-automatic-Annotation-Software-for-Scene-Graph

Zhixuan Zhang, Chi Zhang, Yuehu Liu, Zhenning Niu, Le Wang, Shuqiang Jiang


## Introduction

It is a tool designed for researchers and engineers to annotate scene graph, which is written by python.

![image](teaser_image/UI.png)

### Major Features

- **Friendly user interactivity.**: It has a friendly GUI. Users can visually view the contents annotated and scene graph in real time.
- **Rich annotatable information**: In addition to the relationships between instances, it also allow users to annotate diversified information such as regions, clusters and attributes.
- **Low manpower for annotation**: We designed a semi-automatic annotation module in our system, which can recommend the relationship according to the image information and a priori database. The semi-automatic annotation module greatly improves the annotation efficiency.
- **Strong adaptability**: Users are free to define the underlying data, including object categories, relationship lists and so on. It is help for researchers to build more adaptive datasets.
- **Applying simply**: The output dataset files are organized in VG150's data format and can be directly applied to most existing models for scene graph learning.

### Demo video
TODO


### Software Framework

In this annotation software, there are three core modules: **Main Annotation Module**, **Semi-automatic Annotation Module** and **Auxiliary Function Module**.  Each module is independent of each other. Removing one of the modules does not affect the use of the whole software, which makes it easy for developers to update and maintain.
![image](teaser_image/overview.png)


## Updates

 **25 June 2021:** Our paper will be online.

 **25 June 2021:** Our software will be launched!

## Installation

Please refer to [INSTALL.md](docs/INSTALL.md) for installation and dataset preparation.

## Get Started

Please see [GETTING_STARTED.md](docs/GETTING_STARTED.md) for the basic usage.

## Dataset
We support a scene graph dataset with 1000 traffic images by the annotation software. The images are selected from Cityscapes, which is a pixel-level semantic segmented datasets. In order to show the high variability of traffic scenes, we made efforts to choose images with different features and situations, including crossroad, the tunnel, traffic jam and so on. The steps are: we use places365 to extract the features of the images. Then principal component analysis was used to reduce dimension of features and cluster images into 1000 groups. Images within each group have similar features. Finally, we pick one in each group at random as the original image.
You can download the dataset in https://github.com/Milomilo0320/Traffic-Scene-Graph-1000
## License

This project is released under the [Apache 2.0 license](LICENSE).

## Citation

If you use this toolbox in your research, please cite this paper.
Todo

## Contacts

If you have any questions about our work, please do not hesitate to contact us by emails.

 [zxzhang970320@stu.xjtu.edu.cn](mailto:zxzhang970320@stu.xjtu.edu.cn)

## Acknowledgements

This project is supported by the National Key Research and Development Program of China, No. 2018AAA0102504.





