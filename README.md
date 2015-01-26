# RNNlib Dataset Generator for IAM Handwriting Database

This is a training data generator for [RNNlib](http://sourceforge.net/projects/rnnl/), a recurrent neural network implementation. 
For more information on the network, please refer to the [RNNlib Wiki](http://sourceforge.net/p/rnnl/wiki/Home/). 

## Prerequisites

In order to generate training data, please install **Python**, **Pillow** (PIL) and **NetCDF**. 
Currently, the generator is **nix*-only. 

## Download the IAM Database

All test sequences can be downloaded from the [IAM On-Line Handwriting Database](http://www.iam.unibe.ch/fki/databases/iam-handwriting-database).
Please note, that all data belongs to the University of Bern and requires a login before downloading.
This generator only works with strokes and images from the On-Line database, however it can easily be adapted to work with the Offline database aswell. 

Please consider downloading the following files after registering [here](http://www.iam.unibe.ch/~fkiwww/iamondb/iLogin/index.php):

 - [ascii-all.tar.gz](http://www.iam.unibe.ch/~fkiwww/iamOnDB/data/ascii-all.tar.gz): Plain text transcriptions of all sequences.
 - [lineStrokes-all.tar.gz](http://www.iam.unibe.ch/~fkiwww/iamOnDB/data/lineStrokes-all.tar.gz): XML files containing strokes with timestamps for online recognition.
 - [lineImages-all.tar.gz](http://www.iam.unibe.ch/~fkiwww/iamOnDB/data/lineImages-all.tar.gz): TIF images for offline recognition.

After extracting all archives, the project folder should contain the following files:

```
ascii/
lineImages/
lineStrokes/
build_nc.sh
iam_offline.py
iam_online.py
...
```

After this, download the training set and validation set descriptors for the "Handwritten text recognition task IAM-OnDB-t1". 
These are textfiles that describe which sequences are used for which step in training the RNN. 
Place the text files in the same folder as the extracted archives:

```
ascii/
lineImages/
lineStrokes/
testset_f.txt
testset_t.txt
testset_v.txt
trainset.txt
...
```

## Generate Training Files

The `build_nc.sh` utility creates NetCDF files compatible with RNNlib by processing every sequence in a file list. 
It takes two parameters:

 1. **mode**: Either `online` (uses *lineStrokes/*) or `offline` (uses *lineImages/*). 
 2. **dataset**: The name of a configuration file, e.g. `trainset` or `testset_v` without the `.txt` file extension.

The dataset file contains a list of sample identifiers that is translated into a path depending on the `mode` parameter.
In case one of the files is missing, the script will report an error and continue execution. 
For instance, to process all online samples use the following command:

```
$ /build_nc.sh online trainset
Loading labels
Processing sample a01/a01-020/a01-020x
...
Generating trainset.nc
```

The shell script uses either `iam_online.py` or `iam_offline.py` internally and creates several temporary files with a `CDL` extension. 
Those files are then merged into one `CDL` file and passed to NetCDF to create the training file of the same name. 
Please note, that the temporary CDL files might be slightly larger than the final NetCDF binary.

**NOTE:** In case of an error the CDL files remain in the file system and have to be cleaned up manually. 

## Training RNNlib

The *configs* folder contains sample configurations for both online and offline trainings.
Copy one of these files to the project base directory and run:

```
/path/to/rnnlib --autosave=true <mode>.config
```

The sample configurations use *trainset.nc* for training and *testset_v.nc* and *testset_t.nc* for validation. 
RNNlib usually stops after 200 to 300 epochs with a sequence error rate of about *10%*. 
It generates the following files:

```
online@2015.01.24-18.22.58.736519.best_ctcError.save
online@2015.01.24-18.22.58.736519.best_labelError.save
online@2015.01.24-18.22.58.736519.last.save
online@2015.01.24-18.22.58.736519.log
```

Each save file contains a complete network configuration including internal weights. 
Thus, they can be used to resume training at any point or for classification of new data. 
Please refer to the [RNNlib Wiki](http://sourceforge.net/p/rnnl/wiki/Home/) for more information. 