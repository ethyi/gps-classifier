"""
output_KML
Contains methods used for building a KML file
@author: Ethan Yi | ehy5032@rit.edu
"""


def generate_pin(color, coordinate):
    """
    generates a pin for the stops
    :param color: the color of the pin
    :param coordinate: the coordinate of the pin
    :return: the string to write to the KML file
    """
    output = ""     # output string
    description = ""    # description of pin
    image_url = ""  # the image of the pin
    if color == 'yellow':
        description = "Stop For Errand"
        image_url = 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'
    if color == 'pink':
        description = "Stop/rolling stop for sign or light"
        image_url = "http://maps.google.com/mapfiles/kml/pushpin/pink-pushpin.png"

    output = """    # use KML syntax to make a placemark(the pin)
        <Placemark>
        <description>%s</description>
        <Style id="normalPlacemark">
<IconStyle>
<scale>1.5</scale>
<Icon><href>%s</href></Icon>
</IconStyle>
</Style>
            <Point><coordinates>%s</coordinates></Point>
            </Placemark>
                        """ % (description, image_url, coordinate)
    return output


def generate_path(altitude_data):
    """
    generates the path for the uphill/downhill/flat detection
    :param altitude_data: the altitude data
    :return: the string to write to the KML file
    """
    # various strings for building the KML output
    open_placemark = '<Placemark> '

    open_line = """ 
<LineString>
<coordinates>
    """

    close_all = """
</coordinates>
</LineString>
</Placemark>
"""

    color = ""  # color of the path
    previous = ""   # the previous point
    output = open_placemark + open_line     # the string to write to the KML
    for point in altitude_data:
        # build coordinate
        coordinate = "{},{},{}\n".format(point.longitude, point.latitude, 0)
        if point.color == 'red':
            color = '501400FF'
        elif point.color == 'green':
            color = '5014B400'
        elif point.color == 'cyan':
            color = '50F0FF14'

        # establish style using extracted color
        style = """
                   <Style> 
                   <LineStyle>  
                   <colorMode>normal</colorMode>
                   <color>%s</color>
                   <width>5</width>
                   </LineStyle> 
                   </Style>""" % color

        # if the color has not been repeated, the placemark must be closed,
        # and a new placemark must be made with new color styling
        if previous != color:
            previous = color
            output += close_all
            output += open_placemark
            output += style
            output += open_line

        output += coordinate    # append coordinates in the end

    output += close_all     # close if when there are no more points

    return output


def write_kml(kml_filename, speed_data, altitude_data):
    """
    writes classified coordinates to kml file
    :param kml_filename: the name of the KML file to write to
    :param speed_data: list of points containing speed
    :param altitude_data: list of points containing altitude
    """
    kml_data = []   # list of strings to write to the KML file
    # write speed data
    for point in speed_data:
        # build coordinate
        coordinate = "{},{},{}\n".format(point.longitude, point.latitude,
                                         0)
        if point.color != 'black':  # if color is not the default
            output = generate_pin(point.color, coordinate)
            kml_data.append(output)

    # write altitude data
    output = generate_path(altitude_data)
    kml_data.append(output)

    with open(kml_filename, 'w') as file:
        # write file header
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
    """)
        file.writelines(kml_data)  # write coordinates
        # write file footer
        file.write("""
     </Document>
    </kml>
    """)
