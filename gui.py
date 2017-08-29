import argparse
import wx

# =============================================================================
class MonitorFrame(wx.Frame):
  '''
  Main window for GUI
  '''
  def __init__(self, parent, args):
    size = (args.width, args.height)
    wx.Frame.__init__(self, parent, title='Status Monitor', size=size)
    self.main_panel = wx.Panel(self)
    main_sizer = wx.BoxSizer(wx.VERTICAL)

    # timer
    self.interval = args.interval * 1000  # interval in milliseconds
    self.timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.UpdateView, self.timer)

    # timer button
    self.timer_button = wx.Button(self.main_panel, label='Start')
    self.timer_button.Bind(wx.EVT_BUTTON, self.OnToggleTimer)
    main_sizer.Add(self.timer_button, 0,
                   wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 5)

    # draw
    self.main_panel.SetSizer(main_sizer)

  # ---------------------------------------------------------------------------
  # Event functions
  def OnToggleTimer(self, event=None):
    '''
    Start/Stop monitoring directory
    '''
    if (self.timer.IsRunning()):
      self.timer.Stop()
      self.timer_button.SetLabel('Start')
    else:
      self.timer.Start(self.interval)
      self.timer_button.SetLabel('Stop')

  def UpdateView(self, event=None):
    '''
    Update map and model in Coot, and update statistics
    '''
    pass

# =============================================================================
if (__name__ == '__main__'):

  # comamnd-line arguments for customization
  parser = argparse.ArgumentParser(description='GUI for monitoring progress')
  parser.add_argument('-y', '--height', type=int, default=600,
                      help='height of window')
  parser.add_argument('-x', '--width', type=int, default=800,
                      help='width of window')
  parser.add_argument('-i', '--interval', type=int, default=5,
                      help='time between updates (seconds)')
  parser.add_argument('-d', '--directory', type=unicode, default='.',
                      help='directory to monitor')
  args = parser.parse_args()

  # run GUI
  app = wx.App(False)
  frame = MonitorFrame(None, args)
  frame.Show()
  app.MainLoop()
