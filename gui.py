import argparse
import os
import wx

from wxtbx import bitmaps

# =============================================================================
class file_manager(object):
  '''
  Keeps track of files in a directory
  The file prefix is returned to create the model, map, and JSON files
  '''
  def __init__(self, directory):
    self.directory = directory
    assert (os.path.isdir(self.directory))
    self.file_extensions = ['json', 'pdb', 'mtz']
    self.unique_prefixes = list()
    self.unique_times = list()
    self.current_index = 0

  def update_unique_files(self):
    '''
    check all files and keep those that have all 3 types with the same prefix
    add new files to be tracked, sorted by modification time
    '''
    all_files = os.listdir(self.directory)
    new_prefixes = list()
    for filename in all_files:
      prefix, ext = os.path.splitext(filename)
      if ( (prefix not in self.unique_prefixes) and
           (prefix not in [p[0] for p in new_prefixes]) ):
        complete = True
        for ext in self.file_extensions:
          complete = complete and os.path.isfile(prefix + '.' + ext)
        if (complete):
          test_filename = prefix + '.' + self.file_extensions[0]
          test_filename = os.path.join(self.directory, test_filename)
          new_prefixes.append((prefix, os.path.getmtime(test_filename)))
    if (len(new_prefixes) > 0):
      new_prefixes.sort(key=lambda x: x[1])
      for i in xrange(len(new_prefixes)):
        self.unique_prefixes.append(new_prefixes[i][0])
        self.unique_times.append(new_prefixes[i][1])

  def at_latest(self):
    '''
    Determine if current position is at the most recent file
    '''
    if (self.current_index == (len(self.unique_prefixes) - 1)):
      return True
    return False

  def at_start(self):
    '''
    Determin if current position is at the first file
    '''
    return (self.current_index == 0)

  def get_current(self, full_path=False):
    '''
    Return the file at the current position
    '''
    path = self.unique_prefixes[self.current_index]
    if (full_path):
      path = os.path.join(self.directory, path)
    return path

  def get_latest(self, full_path=False):
    '''
    Return the most recent file and update current position
    None is returned if the current position is already at the end
    '''
    last_index = len(self.unique_prefixes) - 1
    if (self.current_index == last_index):
      return None
    else:
      self.current_index = last_index
      if (self.current_index > -1):
        return self.get_current(full_path)
      else:
        self.current_index = 0
        return None

  def get_previous(self, full_path=False):
    '''
    Return the previous file and update current position
    None is returned if the current position is at the start
    '''
    self.current_index -= 1
    if (self.current_index > -1):
      return self.get_current(full_path)
    else:
      self.current_index = 0
      return None

  def get_next(self, full_path=False):
    '''
    Return the next file and update current position
    None is returned if the current position is at the end
    '''
    self.current_index += 1
    if (self.current_index < len(self.unique_prefixes)):
      return self.get_current(full_path)
    else:
      self.current_index = len(self.unique_prefixes) - 1
      return None

# =============================================================================
class MonitorFrame(wx.Frame):
  '''
  Main window for GUI
  '''
  def __init__(self, parent, args):
    size = (args.width, args.height)
    wx.Frame.__init__(self, parent, title='Status Monitor', size=size)
    main_sizer = wx.BoxSizer(wx.VERTICAL)

    # timer
    self.interval = args.interval * 1000  # interval in milliseconds
    self.timer = wx.Timer(self)
    self.timer.Start(self.interval)
    self.Bind(wx.EVT_TIMER, self.UpdateView, self.timer)
    self.auto_update = True

    # section for progress
    progress_panel = wx.Panel(self, style=wx.SUNKEN_BORDER)
    progress_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.files = file_manager(os.path.abspath(args.directory))
    self.files.update_unique_files()

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
    self.prev_button.Enable(False)
    self.next_button.Enable(False)

    # timer button
    self.auto_button = wx.Button(button_panel, label='Stop')
    self.auto_button.SetBitmap(
      bitmap=bitmaps.fetch_icon_bitmap('actions','stop', scale=self.scale))
    self.auto_button.Bind(wx.EVT_BUTTON, self.OnToggleAuto)

    button_sizer.Add(self.prev_button, 0, wx.ALL, 1)
    button_sizer.Add(self.next_button, 0, wx.ALL, 1)
    button_sizer.AddStretchSpacer()
    button_sizer.Add(self.auto_button, 0, wx.ALL, 5)
    button_panel.SetSizer(button_sizer)

    # draw
    main_sizer.Add(progress_panel, 1, wx.ALL|wx.EXPAND, 5)
    main_sizer.Add(button_panel, 0, wx.ALL|wx.EXPAND, 5)
    self.SetSizerAndFit(main_sizer)
    self.SetMinSize(size)

  def update_view(self, prefix):
    if (prefix is not None):
      print prefix

  def check_next_prev_buttons(self):
    self.prev_button.Enable(True)
    self.next_button.Enable(True)
    if (self.files.at_start()):
      self.prev_button.Enable(False)
    elif (self.files.at_latest()):
      self.next_button.Enable(False)

  # ---------------------------------------------------------------------------
  # Event functions
  def OnToggleAuto(self, event=None):
    '''
    Start/Stop automatic updating
    Next/Prev buttons only work if autoupdate is off
    '''
    # stop monitoring
    if (self.auto_update):
      self.auto_button.SetLabel('Start')
      self.auto_button.SetBitmap(
        bitmap=bitmaps.fetch_icon_bitmap('actions','runit', scale=self.scale))
      self.check_next_prev_buttons()
      self.auto_update = False
    # start monitoring
    else:
      self.auto_button.SetLabel('Stop')
      self.auto_button.SetBitmap(
        bitmap=bitmaps.fetch_icon_bitmap('actions','stop', scale=self.scale))
      self.prev_button.Enable(False)
      self.next_button.Enable(False)
      self.auto_update = True

  def UpdateView(self, event=None):
    '''
    Update tracked files and view if set to automatically update
    '''
    self.files.update_unique_files()
    if (self.auto_update):
      prefix = self.files.get_latest(full_path=True)
      self.update_view(prefix)

  def GetPrev(self, event=None):
    '''
    Update to previous set of files
    '''
    prefix = self.files.get_previous(full_path=True)
    self.check_next_prev_buttons()
    self.update_view(prefix)

  def GetNext(self, event=None):
    '''
    Update to next set of files
    '''
    prefix = self.files.get_next(full_path=True)
    self.check_next_prev_buttons()
    self.update_view(prefix)

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
