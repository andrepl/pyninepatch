# README

pyninepatch is a python library and command line tool for rendering android-style 9-patch images.

## EXAMPLES

### Render a 9-patch to a specific size and display in on screen

#### CLI

    $ python ninepatch.py myninepatch.9.png --size 800x600

#### Python
    >>> import ninepatch, Image
    >>> np = ninepatch.NinePatch("myninepatch.9.png")
    >>> np.render((800,600)).show()


### Render a 9-patch around a content image and save it to disk.

#### CLI

    $ python ninepatch.py myninepatch.9.png --content mycontent.png --output output.png

#### Python

    >>> import ninepatch, Image
    >>> np = ninepatch.NinePatch("myninepatch.9.png")
    >>> img = np.render_around(Image.open("mycontent.png"))
    >>> img.save("output.png")


