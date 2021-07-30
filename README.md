# GPS Movement Classifier

The GPS Movement classifier is a small project I did to test my knowledge of data mining and classification.
It reads in GPS data gathered from driving in car, and classifies if the car ..
- has stopped for parking | Yellow pin
- has stopped for a stop light | Pink pin
- is doing a rolling stop for speedbumps or stop signs | Pink pin
- is going uphill, downhill, or flat | red, green, cyan path

Each classification and its associated color is outputted to a KML file which can be viewed on Google Earth.
I wish I could provide example data but I do not wish to leak my address.

## Installation and Usage
- pynmea2
- numpy
- matplotlib
- scipy 

gps-classifier.py [gps-data filename] [kml output filename]
Only works with GPGGA and GPRMC coordinates. 


## License

MIT