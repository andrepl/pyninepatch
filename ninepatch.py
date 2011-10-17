#!/usr/bin/env python
import Image
import math


class Slice(object):
    """
    represents one section of a 9-patch image.
    
    """
    total_width = 0
    total_height = 0
    def __init__(self, im, x, y, w, h, stretch_x, stretch_y):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.im = im
        self.stretch_x = stretch_x
        self.stretch_y = stretch_y
        
    def set_total_width(self, width):
        self.total_width = width
        self.x_weight = self.w / float(self.total_width)
        
    def set_total_height(self, height):
        self.total_height = height
        self.y_weight = self.h / float(self.total_height)
        
    def __repr__(self):
        return u"<Slice (%s, %s) %sx%s%s%s>" % (self.x, self.y, self.w, self.h, ", Stretch-X" if self.stretch_x else "", ", Stretch-Y" if self.stretch_y else "")
    
    def __str__(self):
        return repr(self)
    
    def __unicode__(self):
        return repr(self)
    
    
class NinePatch(object):
    """
    a 9-Patch image.
    
    
    """

    image = None
    
    def __init__(self, src_im):
        if isinstance(src_im, Image.Image):
            self.image = image
        else:
            self.image = Image.open(src_im)
            
        self._check_image()
        self._slice()
        
    
    def _check_image(self):
        x_stretch_regions = []
        y_stretch_regions = []
        
        x_content_region = None
        y_content_region = None
        
        max_x = self.image.size[0] - 1
        max_y = self.image.size[1] - 1
        
        x_region = None
        y_region = None
        
        pix = self.image.load() # get a pixel access object.
        
        for x in xrange(max_x):
            stretch = pix[x+1, 0][3] != 0
            contentarea = pix[x+1, max_y][3] != 0
            
            # Check for stretchable region
            if x_region is None and stretch:
                x_region = x
            elif isinstance(x_region, int) and not stretch:
                x_stretch_regions.append((x_region, x-1))
                x_region = None
        
            # Check for content region.
            if x_content_region is None and contentarea:
                x_content_region = x
                
            elif isinstance(x_content_region, int) and not contentarea:
                x_content_region = (x_content_region, x-1)
                
            
        if x_content_region is None:
            x_content_region = (0,max_x-1)
            
        
        for y in xrange(max_y):
            stretch = pix[0, y+1][3] != 0
            contentarea = pix[max_x, y+1][3] != 0
            
            # Check for stretchable region
            if y_region is None and stretch:
                y_region = y
            elif isinstance(y_region, int) and not stretch:
                y_stretch_regions.append((y_region, y-1))
                y_region = None
                
            # Check for content region.
            if y_content_region is None and contentarea:
                y_content_region = y
                
            elif isinstance(y_content_region, int) and not contentarea:
                y_content_region = (y_content_region, y-1)
                
            
        if y_content_region is None:
            y_content_region = (0,max_y-1)
        
        self.x_stretch_regions = x_stretch_regions
        self.y_stretch_regions = y_stretch_regions
        self.x_content_region = x_content_region
        self.y_content_region = y_content_region

        self.pad_left = x_content_region[0]
        self.pad_right = self.image.size[0] - x_content_region[1]
        self.pad_top = y_content_region[0]
        self.pad_bottom = self.image.size[1] - y_content_region[1]
        
        # Remove borders.
        self.image = self.image.crop((1,1,max_x-1, max_y-1))
        self.min_width = self.image.size[0] - sum([a[1] - a[0] for a in self.x_stretch_regions])
        self.min_height = self.image.size[1] - sum([a[1] - a[0] for a in self.y_stretch_regions])
        
    def _slice(self):
        xpieces = []
        ypieces = []
        
        for i, xsr in enumerate(self.x_stretch_regions):
            if i == 0:
                xpieces.append((0,xsr[0]-1))
            else:
                xpieces.append((self.x_stretch_regions[i-1][1]+1, xsr[0]-1))
            xpieces.append(xsr)
        xpieces.append((self.x_stretch_regions[-1][1]+1, self.image.size[0]-1))
        
        for i, ysr in enumerate(self.y_stretch_regions):
            if i == 0:
                ypieces.append((0,ysr[0]-1))
            else:
                ypieces.append((self.y_stretch_regions[i-1][1]+1, ysr[0]-1))
            ypieces.append(ysr)
        ypieces.append((self.y_stretch_regions[-1][1]+1, self.image.size[1]-1))
        
    
        gridrows = []
        
        for y,yslice in enumerate(ypieces):
            row = []
            stretch_y = (y % 2 != 0)
            
            for x,xslice in enumerate(xpieces):
                stretch_x = (x % 2 != 0)
                box = (xslice[0], yslice[0], xslice[1], yslice[1])
                im = self.image.crop(box)
                piece = Slice(im, box[0], box[1], im.size[0], im.size[1], stretch_x, stretch_y)
                row.append(piece)
                
            # Calculate horizontal weights
            htotal = sum([p.w for p in row if p.stretch_x])
            for p in row:
                if p.stretch_x:
                    p.set_total_width(htotal)
            gridrows.append(row)
            
        # Calculate Vertical Weights
        vtotal = sum([gridrows[y][0].h for y in xrange(len(gridrows)) if gridrows[y][0].stretch_y])
        for row in gridrows:
            for s in row:
                if s.stretch_y:
                    s.set_total_height(vtotal)
                    
        self.slices = gridrows
        
        
                
    def render(self, size):
        W, H = size
        if W < self.min_width: W = self.min_width
        if H < self.min_height: H = self.min_height
        
        stretchable_width = W - self.min_width
        stretchable_height = H - self.min_height
        
        
        new_im = Image.new("RGBA", (W, H), (0,0,0,0))
        
        y = 0
        for row in self.slices:
            x = 0
            if row[0].stretch_y:
                height = int(row[0].y_weight * stretchable_height)
            else:
                height = row[0].h
            
            for s in row:
                if s.stretch_x:
                    width = int(s.x_weight * stretchable_width)
                else:
                    width = s.w
                new_im.paste(s.im.resize((width, height), Image.NEAREST), (x,y))
                x += width
                
            y += height
        return new_im
            
                
            
    def render_around(self, content_image):
        if not isinstance(content_image, Image.Image):
            content_image = Image.open(content_image)
            
        cw = content_image.size[0]
        ch = content_image.size[1]
        cminw = self.x_content_region[1] - self.x_content_region[0]
        cminh = self.y_content_region[1] - self.y_content_region[0]
        
        if cw < cminw:
            pad_left = self.pad_left + (cminw - cw) / 2
            pad_right = self.pad_right + (cminw - cw) / 2
            
        else:
            pad_left = self.pad_left
            pad_right = self.pad_right
            
        if ch < cminh:
            pad_top = self.pad_top + (cminh - ch) / 2
            pad_bottom = self.pad_bottom + (cminh - ch) / 2
            
        else:
            pad_top = self.pad_top
            pad_bottom = self.pad_bottom
            
        imw = pad_left + pad_right + cw
        imh = pad_top + pad_bottom + ch
        
        im = self.render((imw, imh))
        im.paste(content_image, (pad_left, pad_top), content_image)
        return im
    
            
        

        
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
        
        