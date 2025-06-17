from cyndilib.wrapper.ndi_recv import RecvColorFormat, RecvBandwidth
from cyndilib.finder import Finder, Source
from cyndilib.receiver import Receiver, ReceiveFrameType
from cyndilib.video_frame import VideoFrameSync
from cyndilib.audio_frame import AudioFrameSync
from cyndilib.framesync import FrameSyncThread

class VideoWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Make a blank texture to display when not connected
        bfr = [10 for _ in range(16*9)]
        self._video_update_event = None

    def on_app(self, instance, value):
        self.video_frame_rate = self.app.video_frame.get_frame_rate()
        self.app.bind(connected=self.on_app_connected, on_stop=self.close)

    def on_app_connected(self, instance, value):
        """Start or stop the :meth:`update_video_frame` callbacks
        """
        if value:
            self.start_video_frame_events()
        else:
            self.stop_video_frame_events()
            self.vid_texture = None

    def close(self, *args, **kwargs):
        self.stop_video_frame_events()

    def start_video_frame_events(self, *args):
        """Create a Clock event to repeatedly call :meth:`update_video_frame`
        at an interval matching the :attr:`video_frame_rate`
        """
        self.stop_video_frame_events()
        target_fps = self.video_frame_rate
        interval = float(1 / target_fps)
        evt = Clock.schedule_interval(self.update_video_frame, interval)
        self._video_update_event = evt

    def stop_video_frame_events(self, *args):
        """Stop the Clock event created in :meth:`start_video_frame_events`
        """
        if self._video_update_event is not None:
            Clock.unschedule(self._video_update_event)
            self._video_update_event = None

    def update_video_frame(self, *args):
        """Read a video frame using the :meth:`FrameSync.capture_video` method,
        then update the :attr:`vid_texture`

        The :class:`FrameSync` methods will keep the frame timing as close as
        possible to real time while reducing jitter
        """
        if not self.app.connected:
            return
        self.app.receiver.frame_sync.capture_video()
        vf = self.app.video_frame
        if min(vf.xres, vf.yres) == 0:
            # We haven't received an actual frame yet, do nothing
            return
        # Make sure our video_frame_rate matches the video frame
        fr = vf.get_frame_rate()
        if fr != self.video_frame_rate:
            self.video_frame_rate = fr


class ViewerApp(App):
    finder = ObjectProperty(None, allownone=True)
    """An instance of :class:`cyndilib.finder.Finder`"""

    ndi_source_names = ListProperty([])
    """List of source names discovered by the :attr:`finder`"""

    source_name = StringProperty(None, allownone=True)
    """Name of the source we're currently connected to
    (or ``None`` if not connected)
    """

    source_to_connect_to = StringProperty(None, allownone=True)
    """Name of the source we are attempting to connect to
    (or ``None`` to disconnect)
    """

    source = ObjectProperty(None, allownone=True)
    """The current :class:`cyndilib.finder.Source` object
    (or ``None`` if not connected)
    """

    connected = BooleanProperty(False)
    """Connection state of the :attr:`receiver`"""

    receiver = ObjectProperty(None, allownone=True)
    """An instance of :class:`cyndilib.receiver.Receiver` to handle source
    connection and frame data
    """

    video_frame = ObjectProperty(None)
    """An instance of :class:`cyndilib.video_frame.VideoFrameSync`"""

    audio_frame = ObjectProperty(None)
    """An instance of :class:`cyndilib.audio_frame.AudioFrameSync`"""

    def build(self):
        # Create and start a Finder with a callback
        self.finder = Finder()
        self.finder.set_change_callback(self.on_finder_change)
        self.finder.open()

        # Create a Receiver without a source
        self.receiver = Receiver(
            color_format=RecvColorFormat.RGBX_RGBA,
            bandwidth=RecvBandwidth.highest,
        )
        self.video_frame = VideoFrameSync()
        self.audio_frame = AudioFrameSync()

        # Add the video/audio frames to the receiver's FrameSync
        self.receiver.frame_sync.set_video_frame(self.video_frame)
        self.receiver.frame_sync.set_audio_frame(self.audio_frame)

        self._recv_connect_event = Clock.schedule_interval(self.check_connected, .1)

        # Now build te rest of the widget tree
        w = None
        try:
            w = MainWidget()
        except:
            self.finder.close()
            raise
        return w

    def on_stop(self, *args, **kwargs):
        if self.finder is not None:
            self.finder.close()

    @mainthread
    def on_finder_change(self):
        """Callback for :attr:`finder` called when its list of discovered
        sources has changed

        The :attr:`ndi_source_names` list is updated here

        .. note::

            The callback exists in a separate thread. In Kivy, there's a
            convenience decorator to handle it within the main thread, but
            UI frameworks vary.
        """
        if self.finder is None:
            return
        self.ndi_source_names = self.finder.get_source_names()
        self.update_source()

    def on_source_to_connect_to(self, *args):
        self.update_source()

    def update_source(self, *args):
        """Look for a source matching the :attr:`source_to_connect_to` string
        and set that as the current :attr:`source`

        This is called when changes to :attr:`ndi_source_names` or
        :attr:`source_to_connect_to` changes.

        We use the :attr:`finder` to get the :class:`~cyndilib.finder.Source`
        object, but acquire its lock to ensure it doesn't update while doing so.
        """
        if self.source_to_connect_to is None:
            self.source = None
        else:
            with self.finder.notify:
                self.source = self.finder.get_source(self.source_to_connect_to)

    def on_source(self, *args):
        """Set the receiver's source to our current :attr:`source`
        (can be a valid :class:`~cyndilib.finder.Source` object or None to disconnect)
        """
        self.receiver.set_source(self.source)
        if self.source is None:
            self.source_name = None
        else:
            self.source_name = self.source.name

    def check_connected(self, *args):
        self.connected = self.receiver.is_connected()

if __name__ == '__main__':
    ViewerApp().run()
