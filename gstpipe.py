import gst
import pygtk
import gtk
from daemon import become_daemon

pipeline = gst.Pipeline('mypipeline')

wavefile = gst.element_factory_make('filesink')
wavefile.set_property('location', 'test.wav')
pipeline.add(wavefile)


encoder = gst.element_factory_make('ffenc_libfaac')
pipeline.add(encoder)

muxer = gst.element_factory_make('ffmux_mpegts')
pipeline.add(muxer)

sink = gst.element_factory_make('tcpclientsink')
sink.set_property('host', '127.0.0.1')
sink.set_property('port', 9999)
pipeline.add(sink)

#alsasrc.link(wavepack)
#wavepack.link(wavefile)

wavefile.link(encoder)
encoder.link(muxer)
muxer.link(sink)

pipeline.set_state(gst.STATE_PLAYING)

#become_daemon()
gtk.main()
