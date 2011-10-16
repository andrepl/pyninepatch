import re
import os, sys
import Image


class NinePatch(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.image = Image.open(filename)
        self.pix = self.image.load()
        self.scan_border()
        
        
    def scan_border(self):        
        ## Scan top and left borders to determine slices.
        horiz = []
        vert = []
        for x in xrange(self.image.size[0]):
            marked = self.pix[x,0][3] != 0
            if not horiz and marked:
                horiz.append(x-1)
            elif horiz and not marked:
                horiz.append(x-1)
        for y in xrange(self.image.size[1]):
            marked = self.pix[0,y][3] != 0
            if not vert and marked:
                vert.append(y-1)
            elif vert and not marked:
                vert.append(y-1)
        
        self.horiz = horiz
        self.vert = vert
        
        self.top_left = self.image.crop((1,1,horiz[0],vert[0]))
        self.top_center = self.image.crop((horiz[0], 1, horiz[1], vert[0]))
        self.top_right = self.image.crop((horiz[1], 1, self.image.size[0]-2, vert[0]))
        
        self.center_left = self.image.crop((1,vert[0], horiz[0], vert[1]))
        self.center = self.image.crop((horiz[0],vert[0], horiz[1], vert[1]))
        self.center_right = self.image.crop((horiz[1], vert[0], self.image.size[0]-2, vert[1]))
        
        self.bottom_left = self.image.crop((1, vert[1], horiz[0], self.image.size[1]-2))
        self.bottom_center = self.image.crop((horiz[0], vert[1], horiz[1], self.image.size[1]-2))
        self.bottom_right = self.image.crop((horiz[1], vert[1], self.image.size[0]-2, self.image.size[1]-2))
        
        ## Scan right and bottom edges to determine content padding.
        self.pad_top = 0
        self.pad_left = 0
        self.pad_right = 0
        self.pad_bottom = 0
        for x in xrange(self.image.size[0]):
            marked = self.pix[x,self.image.size[1]-1][3] != 0
            if not self.pad_left and marked:
                self.pad_left = x-2
            elif self.pad_left and (not marked) and (not self.pad_right):
                self.pad_right = (self.image.size[0]-1) - (x-1)
            
        for y in xrange(self.image.size[1]):
            marked = self.pix[self.image.size[0]-1,y][3] != 0
            if not self.pad_top and marked:
                self.pad_top = y-2
            elif self.pad_top and (not marked) and (not self.pad_bottom):
                self.pad_bottom = (self.image.size[1]-1) - (y-1)
           
        
    def render(self, size):
        x_stretch = size[0] - (self.top_left.size[0] + self.top_right.size[0])
        y_stretch = size[1] - (self.top_left.size[1] + self.bottom_left.size[1])
        im = Image.new("RGBA", size, (0,0,0,0))
        #top left
        im.paste(self.top_left,(0,0))
        #top center
        tc = self.top_center.resize((x_stretch, self.top_center.size[1]))
        im.paste(tc, (self.top_left.size[0], 0))
        
        #top right
        im.paste(self.top_right, (self.top_left.size[0] + x_stretch -1, 0))
        
        #center left
        cl = self.center_left.resize((self.top_left.size[0],y_stretch))
        im.paste(cl, (0,self.top_left.size[1]))
        
        #center center
        cc = self.center.resize((x_stretch, y_stretch))
        im.paste(cc, (self.top_left.size[0], self.top_left.size[1]))
        
        #center right
        cr = self.center_right.resize((self.top_right.size[0], y_stretch))
        im.paste(cr, (self.top_left.size[0] + x_stretch -1, 
                      self.top_left.size[1]-1))
        
        #bottom left
        im.paste(self.bottom_left, 
                 (0, self.top_left.size[1] + y_stretch - 1))
        
        #bottom center
        bc = self.bottom_center.resize((x_stretch, self.bottom_center.size[1]))
        im.paste(bc, (self.top_left.size[0]-1,
                      self.top_left.size[1] + y_stretch -1))
        
        #bottom right
        im.paste(self.bottom_right, (self.top_left.size[0] + x_stretch - 1,
                                     self.top_left.size[1] + y_stretch -1))
        return im
        
        
    def render_around(self, image):
        
        minwidth = self.top_left.size[0] + self.top_right.size[0]
        minheight = self.top_left.size[1] + self.bottom_left.size[1]
        w = image.size[0] + self.pad_left + self.pad_right
        h = image.size[1] + self.pad_top + self.pad_bottom        
        pad_left = self.pad_left
        pad_top = self.pad_top
        pad_right = self.pad_right
        pad_bottom = self.pad_bottom
        
        if w < minwidth: 
            pad_left += (minwidth - w) / 2
            pad_right += (minwidth - w) / 2
            w = minwidth
        if h < minheight:
            pad_top += (minheight - h) / 2
            pad_bottom += (minheight -h) /2 
            h = minheight
        bg = self.render((w,h))
        bg.paste(image, (pad_left, pad_top))
        return bg
    
    
        
def parse_size(sizeS):
    return tuple(map(int, re.split("x", sizeS, re.I)))
                    
if __name__ == "__main__":
    import sys
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-s", "--size", dest="size")
    parser.add_option("-c", "--content", dest="content")
    parser.add_option("-o", "--output", dest="output")
    opts, args = parser.parse_args()
    
    if opts.size is None and opts.content is None:
        print "You must specify one of --size or --content"
        sys.exit(2)
        
    if len(args) < 1:
        print "You must specify the path to the 9 patch texture"
        sys.exit(3)
    
    
    np = NinePatch(args[0])
    
    if opts.content:
        content_im = Image.open(opts.content)
        result = np.render_around(content_im)
    else:
        result = np.render(parse_size(opts.size))
        
        
    if opts.output:
        result.save(opts.output)
    else:
        result.show()
        
        
    
    
    
    
    
    
