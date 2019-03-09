<header> 
    <font size="6">
    Directory Contents
    </font>
</header>

* driver: This contains many "drivers" for driving the Jove functionality.
  Thus, for example,
  you will find Drive_DFA.ipynb inside driver/. It helps drive the
  contents of Def_DFA.ipynb inside src/. This cleanly separates out the
  basic definitions pertaining to DFA (contained inside Def_..) from how
  a user might use it (contained inside Drive_...)

* module: The contents of this directory were written in the early
  days of developing Jove (before I wrote the Jove markdown translator).
  Still it is quite educational. The notebooks in this directory
  are more self-contained

  Continuing with
  our example above, Module3_DFA.ipynb contains some definitions from
  Def_DFA.ipynb followed by some commands to drive (similar to those in
  Drive_DFA.ipynb). The syntax used in these notebooks is the older one
  where we don't illustrate the Jove markdown (e.g., and so DFA are
  specified in the baroque syntax of Python dictionaries)

* src: These are the .ipynb notebooks that help generate .py files for
  inclusion in various other notebooks.

* tutorial: These are various single-topic tutorials (often containing
  Youtube videos) on how to use Jove. These may pertain to lectures I've
  given on specific days, and illustrates what a class-room activity
  using Jove might consist of. You must begin with First\_Jove\_Tutorial
  in any case, to obtain quick orientation of the topics

# END
