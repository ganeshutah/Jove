<header> 
    <font size="6">
    Jove's colab documentation -- run Jove without installing anything!
    </font>
</header>


# Introduction

  These notes pertain to using Jove on Google's 'colab' facility.
  It helps anyone use Jove without installing Jupyter notebooks!
  
  These runs are done by referring to Jove's github but the colab branch.
  Please point to the colab branch (the other branches won't work).
  
  Here is how you get started:

  1. Make a folder "My Drive/CS3100Spring20", or your chosen name.
  
  2. cd to CS3100Spring20, and
  
  3. git clone https://github.com/ganeshutah/Jove.git in here

     ** I have found that only the contents of Jove/jove are necessary **

     ** However you may wish to have also the Jove/machines subdir for prebuilt machines **
     
     Then you can load machines as follows (for example):
     
     dped1 = md2mc(src="File",
      fname="/content/gdrive/My Drive/CS3100Spring20/Jove/machines/dfafiles/pedagogical1.dfa") 

     You may delete the other files!

  4. Then proceed with browsing
    http://colab.research.google.com/github/googlecolab/colabtools/blob/master

    ( abbreviated for your convenience as bit.ly/colab_jove )
    
    and give the Github path https://github.com/ganeshutah/Jove.git

    and do switch to the colab branch

  5. Begin working with any of the notebooks you see in here.

     You will be prompted to obtain an authorization code from a certain URL

     Give the necessary permissions, and the code will be revealed. Click, copy,
     and bring it to your main buffer and enter it there where it says
     "Enter your authorization code".

     It then mounts the right files.

     a. File -> Open Notebook -> On Github

     b. Point to ganeshutah/Jove.git (full path needn't be given; colab finds the actual github)

     c. Switch to the colab branch


  6. You can see the Jupyter sessions in vogue, stop any session (especially
     if you exceed the number of sessions), etc.

  7. You may also browse files on Github and run them in the colab mode

  8. "My Drive" will have a folder called "Colab Notebooks" that will contain
     notebooks that you save. Further save/load options on Google Drive or
     Github is available.

  9. Handy commands:

     a. Tools -> Command Palette -> Clear [ brings up clear all outputs ]

     b. Intellisense-like popping up of functions already loaded

     	i. Just type "dfa" in an empty cell, and it brings up all commands
	   that carry the substring "dfa" in them

Further notes on colab will be provided in due course.
