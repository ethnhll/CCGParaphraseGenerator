CCGParaphraseGenerator
======================
Adapting statistical parsers to new domains requires annotated data, which is expensive and time consuming to collect.
Using crowd-sourced annotation data as a “silver standard” is a step towards a more viable solution and so in order to
facilitate the collection of this data, we have developed a system for creating semantic disambiguation tasks for use
in crowd-sourced judgments of meaning. In our system, these tasks are generated automatically using surface
realizations of structurally ambiguous parse trees, along with minimal use of forced parse structure changes.

Installation
------------
There are several external dependencies to this package, and for now this package is
really only supported on _NIX based OSes.

This package is heavily dependent on [OpenCCG](https://github.com/OpenCCG/openccg) and requires very specific
instructions for installing to work properly with CCGParaphraseGenerator.


### OpenCCG
Follow all instructions for [installing OpenCCG](https://github.com/OpenCCG/openccg#README) and then perform the
additional requirements laid out below.

1.  If they are not mentioned in the instructions from above, do make sure to follow the instructions for
dependency installations for [KenLM](https://kheafield.com/code/kenlm/dependencies/).

2.  Follow the instructions found [here](https://github.com/OpenCCG/openccg/blob/master/docs/ccgbank-README) for
installing language models and the Stanford Core NLP libraries (sections: "Introduction", "Using the pre-built English
models", "Installing the Stanford Core NLP tools")

For now, there is an additional code change in OpenCCG that is required by CCGParaphraseGenerator which allows
it to make use of parse trees when referencing surface realizations. As the binary hosted on SourceForge for OpenCCG is
updated to include the latest code changes from Github, this step will no longer be necessary.

3.  Download the source code for OpenCCG `git clone https://github.com/OpenCCG/openccg.git` and merge the source code
with the source downloaded from SourceForge, overwriting any conflicts with the files from Github. The new source must
now be recompiled. First remove the output folder which contains the compiled java classes for the project,
`rm -rf $OPENCCG_HOME/output` and then execute the build to recompile `cd $OPENCCG_HOME ; ccg-build`

4.  Now, you will need to add change a few sections of a build file to complete the installation as
CCGParaphraseGenerator requires it. Open $OPENCCG_HOME/ccgbank/build-rz.xml in your favorite editor and under the
"Testing" section, look for the targets with names "test-realizer", "test-realizer-perceptron",
"test-realizer-perceptron-23", and "test-realizer-novel". In the `<exec ...>` element for each of those targets, add
`<arg value="-nbestincludelfs"/>` to the list of arguments.

### CCGParaphraseGenerator
Now for the tool itself, simply clone the repository in any directory you want.

`git clone https://github.com/hill1303/CCGParaphraseGenerator.git`

Usage
-----

To use CCGParaphraseGenerator, `cd` into the directory where you cloned the repository from earlier, and from there
`cd CCGParaphraseGenerator` to begin using the tool.

In general when using the tool, you must execute it as the python module called novel_disambiguation (using Python2.7,
currently Python3 is not supported) like so, `python -m novel_disambiguation --OPTION <VALUE>`

_NOTE_: Make sure that if you want to keep record of previous runs for this application (ie logs) to back these up from the
directory `CCGParaphraseGenerator/novel_disambiguation/logs/`

#### Help
To display a help view, enter `python -m novel_disambiguation --help` or `python -m novel_disambiguation -h`

#### Processing Text
When running this tool, there is a required argument after the name of the module which specifies where the text files
to process live, relative to the directory "$OPENCCG_HOME/ccgbank". For example, if you wanted to process files in
"$OPENCCG_HOME/ccgbank/data/novel_text/" you would issue this command: `python -m novel_disambiguation data/novel_text`

By default, running the aforementioned command will parse and generate realizations for the input text.
If this has already been done before and the generated files still exist, one can skip parsing and realization
by issuing the same command with the "-pp" or "--post-process" option, like so
`python -m novel_disambiguation data/novel_text -pp`

There are several other options specified in the help text for this program which provide options for specifying text
files for processing (either by inclusion with a list or file containing a list, or by exclusion with the same kind of
list).

Bug Reporting
=============
If you notice a bug or have commentary for improvements/changes, please open an issue for it on Github. I'll do what I
can to fix it. If you're awesome, you can provide the fix yourself and submit a pull request which I'll review and
likely approve right away :P
