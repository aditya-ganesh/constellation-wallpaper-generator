import svgmanip as svg
import cairosvg as cairo
from string import digits
from random import choice
from lxml.etree import Element,XML
from copy import deepcopy


strip_tag = lambda x : x.replace("{http://www.w3.org/2000/svg}","")

SVG_ELEMENTS = [
    "path",
    "rect",
    "circle",
    "ellipse",
    "line",
    "polyline",
    "polygon"
]

class Canvas:
    
    bloom_filter_def = """
    <filter id="glow">
        <feGaussianBlur
        in="SourceGraphic"
        stdDeviation="10"
        result="glow__svg__blur"
        id="glow__svg__res"
        />
        <feBlend
        mode="lighten"
        in="SourceGraphic"
        in2="glow__svg__blur"
        />
    </filter>
    """
    bloom = XML(bloom_filter_def)

    def __init__(self,width: float, height: float) -> None:
        """
        Create a canvas with a magic (white) background to add elements onto.
        Given that the canvas is ultimately going to be converted into a PNG,
        you might want to pass PNG resolution as dimensions anyway.

        Args:
            width (int): canvas width
            height (int): canvas height
        """


        self.canvas = svg.Element(width,height)
        
        self.background = svg.Element(width,height)
        self.detail     = svg.Element(width,height)
        self.foreground = svg.Element(width,height)
        
        self.width = width
        self.height = height

        background_id = ''.join(choice(digits) for _ in range(4))

        background = Element("rect",
                            id="rect{}".format(background_id),
                            width="{}".format(width),
                            height="{}".format(height),
                            x="0",
                            y="0",
                            style="fill:#ffffff;stroke:none;")


        self.background.root.append(background)


        self.aspect_ratio = width/height

    def scale_object( self,
                     obj : svg.Element,
                     scale: float) -> tuple:
        """
        Scale an object BY VALUE in  relation to the canvas

        Args:
            object (svg.Element): Element to scale
            scale (float): Fraction of the canvas size (0->1)
        
        Returns:
            tuple : Scaled object and its corresponding scale factor
        """

        obj = deepcopy(obj)
        scale_using_width = True if obj.width > obj.height else False

        if scale_using_width:
            factor = scale * self.width / obj.width
        else:
            factor = scale * self.height / obj.height
        
        obj.scale(factor)

        return obj,factor

    @staticmethod
    def set_object_alpha(obj: svg.Element, 
                         fill_alpha : float = 1,
                         stroke_alpha : float = 1) -> svg.Element:


        obj = deepcopy(obj)
        descendants = obj.root.iterdescendants()
        for descendant in descendants:
            if strip_tag(descendant.tag) in SVG_ELEMENTS:
                style = descendant.get('style')
                style = style + f";fill-opacity:{fill_alpha};stroke-opacity:{stroke_alpha}"
                descendant.set("style",style)
        
        return obj


    def get_centre_coordinates( self,
                                obj : svg.Element,
                                scale: float = 1) -> tuple:
        """
        Given an object, calculate and return the coordinates to place it at the centre of the canvas

        Args:
            object (svg.Element): Object to centre

        Returns:
            tuple: Calculated x,y coordinates
        """

        x = (self.width-(obj.width*scale))/2
        y = (self.height-(obj.height*scale))/2

        return (x,y)


    def place_object(   self,
                        obj : svg.Element,
                        x: float,
                        y : float,
                        layer: str = "foreground") -> None:
        """
        Place an object BY VALUE on the canvas at a given x,y

        Args:
            object (svg.Element): The object to place
            x (float): x-coord
            y (float): y-coord
        """
            
        obj = deepcopy(obj)
        match layer:
            case "foreground":
                self.foreground.placeat(obj,x,y)
            case "detail":
                self.detail.placeat(obj,x,y)

    def export(self, path: str) -> None:
        self.compose()
        cairo.svg2png(  bytestring=self.canvas.tostr(),
                        write_to=path,
                        parent_width=self.width,
                        parent_height=self.height,
                        scale=1)
    
    def dumps(self) -> str:
        self.compose()
        return self.canvas.tostr()
    
    def dump(self,path: str) -> None:
        self.compose()
        self.canvas.dump(path)

    def compose(self) -> None:
        self.canvas.placeat(self.background,0,0)
        self.canvas.placeat(self.detail,0,0)
        self.canvas.placeat(self.foreground,0,0)

    def transform_alpha(self,current_alpha:float,target_alpha:float) -> None:
        for obj in [self.background,self.detail,self.foreground]:
            descendants = obj.root.iterdescendants()
            for descendant in descendants:
                if strip_tag(descendant.tag) in SVG_ELEMENTS:
                    style = descendant.get('style')
                    style = style.replace(f"fill-opacity:{current_alpha}",f"fill-opacity:{target_alpha}")
                    descendant.set('style',style)


    def transform_colours(self,transform_colour_dict: dict) -> None:
        """
        
        Given an SVG drawing and a colour transformation dictionary,
        replace all colours with their maps

        Args:
            drawing (svg.Element): An SVG drawing
            transform_colour_dict (dict): A dictionary of colour transformations expressed as
            {
                "#<some-colour-to-replace>" : "#<target-colour>"
            }
        """
        for obj in [self.background,self.detail,self.foreground]:
            descendants = obj.root.iterdescendants()
            for descendant in descendants:
                if strip_tag(descendant.tag) in SVG_ELEMENTS:
                    style = descendant.get('style')
                    for key in transform_colour_dict.keys():
                        style = style.replace(key,transform_colour_dict[key])
                    descendant.set('style',style)




