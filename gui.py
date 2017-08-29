import argparse
import os
import wx

from wxtbx import bitmaps

# =============================================================================
class MonitorFrame(wx.Frame):
  '''
  Main window for GUI
  '''
  def __init__(self, parent, args):
    size = (args.width, args.height)
    wx.Frame.__init__(self, parent, title='Status Monitor', size=size)
    # self.main_panel = wx.Panel(self)
    main_sizer = wx.BoxSizer(wx.VERTICAL)

    # timer
    self.interval = args.interval * 1000  # interval in milliseconds
    self.timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.UpdateView, self.timer)

    # section for progress
    progress_panel = wx.Panel(self, style=wx.SUNKEN_BORDER)
    progress_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.directory = os.path.abspath(args.directory)
    progress_panel.SetSizer(progress_sizer)

    # subsection for Table 1

    # subsection for Table 2 graph

    # section for buttons
    button_panel = wx.Panel(self, style=wx.SUNKEN_BORDER)
    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.scale = (24,24)

    # Next/Previous buttons
    self.prev_button = wx.BitmapButton(
      button_panel,bitmap=bitmaps.fetch_icon_bitmap('actions','back'))
    self.next_button = wx.BitmapButton(
      button_panel, bitmap=bitmaps.fetch_icon_bitmap('actions','forward'))
    self.prev_button.Bind(wx.EVT_BUTTON, self.GetPrev)
    self.next_button.Bind(wx.EVT_BUTTON, self.GetNext)

    # timer button
    self.timer_button = wx.Button(button_panel, label='Start')
    self.timer_button.SetBitmap(
      bitmap=bitmaps.fetch_icon_bitmap('actions','runit', scale=self.scale))
    self.timer_button.Bind(wx.EVT_BUTTON, self.OnToggleTimer)

    button_sizer.Add(self.prev_button, 0, wx.ALL, 1)
    button_sizer.Add(self.next_button, 0, wx.ALL, 1)
    button_sizer.AddStretchSpacer()
    button_sizer.Add(self.timer_button, 0, wx.ALL, 5)
    button_panel.SetSizer(button_sizer)

    # draw
    main_sizer.Add(progress_panel, 1, wx.ALL|wx.EXPAND, 5)
    main_sizer.Add(button_panel, 0, wx.ALL|wx.EXPAND, 5)
    self.SetSizerAndFit(main_sizer)
    self.SetMinSize(size)

  # ---------------------------------------------------------------------------
  # Event functions
  def OnToggleTimer(self, event=None):
    '''
    Start/Stop monitoring directory
    Next/Prev buttons only work if timer is off
    '''
    # stop monitoring
    if (self.timer.IsRunning()):
      self.timer.Stop()
      self.timer_button.SetLabel('Start')
      self.timer_button.SetBitmap(
        bitmap=bitmaps.fetch_icon_bitmap('actions','runit', scale=self.scale))
      self.prev_button.Enable(True)
      self.next_button.Enable(True)
    # start monitoring
    else:
      self.timer.Start(self.interval)
      self.timer_button.SetLabel('Stop')
      self.timer_button.SetBitmap(
        bitmap=bitmaps.fetch_icon_bitmap('actions','stop', scale=self.scale))
      self.prev_button.Enable(False)
      self.next_button.Enable(False)

  def UpdateView(self, event=None):
    '''
    Update map and model in Coot, and update statistics
    '''
    pass

  def GetPrev(self, event=None):
    '''
    Update to previous set of files
    '''
    pass

  def GetNext(self, event=None):
    '''
    Update to next set of files
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
