# Ambilights (Under Development)
DIY code for PC-based active ambient lighting. Commands addressable LEDs (Adafruit Neopixels) in real time to mirror display. 

PC runs openCV processing to determine standout colors in submatrices using k-means clustering. Color data is compiled and serially communicated to Microcontroller.
  Updates in real time with configurable display dimensions, # of subregions, refresh rate, and others.
  Stores RGB color tuples in numpy array representative of LED layout.

Color data is restructured for ease of addressability. LEDs are assigned colors based from matrix structure and activated via D-OUT.
  Uses Arduino Uno clone and external power supply.

  # TODO
  Build GUI application to make live changes to configuration and control
    Change brightness, effects, solid color
    Start/stop/reset process and communication
    Use PyInstaller [or similar] to build .bat or .exe script implementation
