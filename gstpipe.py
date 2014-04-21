import pygst
import gst
import pygtk
import gtk

pipeline = gst.Pipeline('mypipeline')

filesrc = gst.element_factory_make('filesrc')
filesrc.set_property('location', 'test.mp3')
pipeline.add(filesrc)

encoder = gst.element_factory_make('mp3parse')
pipeline.add(encoder)

muxer = gst.element_factory_make('ffmux_mpegts')
pipeline.add(muxer)

sink = gst.element_factory_make('tcpclientsink')
sink.set_property('host', '127.0.0.1')
sink.set_property('port', 9999)
pipeline.add(sink)


filesrc.link(encoder)
encoder.link(muxer)
muxer.link(sink)

pipeline.set_state(gst.STATE_PLAYING)

gtk.main()