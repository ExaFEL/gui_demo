import argparse
import json
import os
import wx

import libtbx.load_env
from libtbx import xmlrpc_utils
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
          complete = complete and os.path.isfile(
            os.path.join(self.directory, prefix + '.' + ext))
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
    Determine if current position is at the first file
    '''
    return (self.current_index == 0)

  def get_current(self, full_path=False):
    '''
    Return the file at the current position
    '''
    path = None
    if (len(self.unique_prefixes) > 0):
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
class TableOneWidgets(object):

  def __init__(self, parent, sizer):
    '''
    Container for widgets for Table 1 data
    '''

    self.parent = parent
    self.sizer = sizer
    self.sizer.SetRows(28)
    self.sizer.SetCols(2)

    self.collection_widgets = dict()     # split widgets because of Resolution
    self.refinement_widgets = dict()

    # items with multiple values
    self.unit_cell = dict()
    self.uc_labels = ('a', 'alpha', 'b', 'beta', 'c', 'gamma')
    self.no_atoms = dict()
    self.plw_labels = ('Protein', 'Ligand/ion', 'Water')
    self.b_factors = dict()
    self.rms = dict()
    self.rms_labels = ('Bond lengths', 'Bond angles')
    self.rama = dict()
    self.rama_labels = ('Favored', 'Outliers')

    self.sizer.Add(
      self.set_bold(wx.StaticText(parent, label='Data Collection:')),
      0, wx.ALIGN_LEFT, 0)
    self.sizer.AddStretchSpacer()

    # headings from JSON, maybe read from file instead
    for label in ('Space group', 'Cell dimensions', 'Resolution', 'Rsplit',
                  'I/sigI', 'Completeness', 'Multiplicity (Stills)',
                  'No. collected images', 'No. images used',
                  'No. lattices merged', 'No. total reflections',
                  'CC1/2', 'CCiso', 'CC*', 'CCano', 'Wilson B factor'):
      self.add_row(label, self.collection_widgets)

    self.sizer.AddStretchSpacer()
    self.sizer.AddStretchSpacer()

    self.sizer.Add(
      self.set_bold(wx.StaticText(parent, label='Refinement:')),
      0, wx.ALIGN_LEFT, 0)
    self.sizer.AddStretchSpacer()

    for label in ('Resolution', 'Rwork / Rfree', 'No. atoms',
                  'B-factors', 'R.m.s deviations', 'Clashscore',
                  'Ramachandran statistics'):
      self.add_row(label, self.refinement_widgets)

  def set_bold(self, text_widget):
    bold_font = text_widget.GetFont()
    bold_font.SetWeight(wx.FONTWEIGHT_BOLD)
    text_widget.SetFont(bold_font)
    return text_widget

  def add_row(self, label, widgets, sizer=None):
    '''
    Layout widgets
    '''
    if (sizer is None):
      sizer = self.sizer
    new_label = label + ': '
    sizer.Add(
      self.set_bold(wx.StaticText(self.parent, label=new_label)),
      0, wx.ALIGN_RIGHT, 0)
    # special widgets for rows with multiple values
    if (label == 'Cell dimensions'):
      new_sizer = wx.FlexGridSizer(rows=3, cols=4)
      for sublabel in self.uc_labels:
        self.add_row(sublabel, self.unit_cell, new_sizer)
      widgets[label] = new_sizer
    elif (label == 'No. atoms'):
      new_sizer = wx.FlexGridSizer(rows=3, cols=2)
      for sublabel in self.plw_labels:
        self.add_row(sublabel, self.no_atoms, new_sizer)
      widgets[label] = new_sizer
    elif (label == 'B-factors'):
      new_sizer = wx.FlexGridSizer(rows=3, cols=2)
      for sublabel in self.plw_labels:
        self.add_row(sublabel, self.b_factors, new_sizer)
      widgets[label] = new_sizer
    elif (label == 'R.m.s deviations'):
      new_sizer = wx.FlexGridSizer(rows=2, cols=2)
      for sublabel in self.rms_labels:
        self.add_row(sublabel, self.rms, new_sizer)
      widgets[label] = new_sizer
    elif (label == 'Ramachandran statistics'):
      new_sizer = wx.FlexGridSizer(rows=2, cols=2)
      for sublabel in self.rama_labels:
        self.add_row(sublabel, self.rama, new_sizer)
      widgets[label] = new_sizer
    else:
      widgets[label] = wx.StaticText(self.parent, label='N/A')
    sizer.Add(widgets[label], 0, wx.ALIGN_RIGHT, 0)

  def update_values(self, t1):
    '''
    Given a parsed JSON object, t1, update the values in the widget
    '''
    t_dc = t1['Data collection']
    for label in t_dc.keys():
      t = t_dc[label]
      if (label == 'Cell dimensions'):
        for sublabel in self.uc_labels:
          self.update_widget(sublabel, self.unit_cell, t[sublabel])
      else:
        self.update_widget(label, self.collection_widgets, t)

    t_r = t1['Refinement']
    for label in t_r.keys():
      t = t_r[label]
      if (label == 'No. atoms'):
        for sublabel in self.plw_labels:
          self.update_widget(sublabel, self.no_atoms, t[sublabel])
      elif (label == 'B-factors'):
        for sublabel in self.plw_labels:
          self.update_widget(sublabel, self.b_factors, t[sublabel])
      elif (label == 'R.m.s deviations'):
        for sublabel in self.rms_labels:
          self.update_widget(sublabel, self.rms, t[sublabel])
      elif (label == 'Ramachandran statistics'):
        for sublabel in self.rama_labels:
          self.update_widget(sublabel, self.rama, t[sublabel])
      else:
        self.update_widget(label, self.refinement_widgets, t)

  def update_widget(self, label, widgets, text):
    '''
    Change the text of an individual widget
    '''
    if ( not (isinstance(text, unicode) or isinstance(text, str)) ):
      try:
        text = unicode(text)
      except Exception:
        text = 'N/A'
    widgets[label].SetLabel(text)

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
    progress_sizer = wx.BoxSizer(wx.VERTICAL)
    self.files = file_manager(os.path.abspath(args.directory))
    self.files.update_unique_files()

    # subsection of file information
    file_info_sizer = wx.FlexGridSizer(rows=2, cols=2)
    directory_label = wx.StaticText(progress_panel, label='Directory: ')
    directory_text = wx.StaticText(
      progress_panel, label=os.path.abspath(args.directory))
    bold_font = directory_label.GetFont()
    bold_font.SetWeight(wx.FONTWEIGHT_BOLD)
    directory_label.SetFont(bold_font)
    file_label = wx.StaticText(progress_panel, label='File prefix: ')
    file_label.SetFont(bold_font)
    file_text = self.files.get_current()
    if (file_text is None):
      file_text = ''
    self.file_text = wx.StaticText(progress_panel, label=file_text)
    file_info_sizer.Add(directory_label, 0, wx.ALIGN_RIGHT, 0)
    file_info_sizer.Add(directory_text, 0, wx.EXPAND|wx.ALIGN_LEFT, 0)
    file_info_sizer.Add(file_label, 0, wx.ALIGN_RIGHT, 0)
    file_info_sizer.Add(self.file_text, 0, wx.EXPAND|wx.ALIGN_LEFT, 0)

    # subsection for Table 1
    data_sizer = wx.BoxSizer(wx.HORIZONTAL)
    t1_sizer = wx.FlexGridSizer()
    self.t1 = TableOneWidgets(progress_panel, t1_sizer)

    # subsection for Table 2 graph
    t2_sizer = wx.FlexGridSizer(rows=28, cols=2)
    self.t2 = TableOneWidgets(progress_panel, t2_sizer)

    data_sizer.Add(t1_sizer, 0, wx.ALL, 5)
    data_sizer.Add(
      wx.StaticLine(progress_panel, size=(20, 20), style=wx.LI_VERTICAL),
      0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM|wx.EXPAND, 25)
    data_sizer.Add(t2_sizer, 1, wx.EXPAND|wx.ALL, 0)

    # layout data panel
    progress_sizer.Add(file_info_sizer, 0, wx.ALL|wx.EXPAND, 5)
    progress_sizer.Add(
      wx.StaticLine(progress_panel, size=(args.width-50, 4),
                    style=wx.LI_HORIZONTAL),
      0, wx.LEFT|wx.RIGHT|wx.EXPAND, 25)
    progress_sizer.Add(data_sizer, 1, wx.ALL|wx.EXPAND, 5)
    progress_panel.SetSizer(progress_sizer)

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

    # toggle autoupdate button
    self.auto_button = wx.Button(button_panel, label='Stop')
    self.auto_button.SetBitmap(
      bitmap=bitmaps.fetch_icon_bitmap('actions','stop', scale=self.scale))
    self.auto_button.Bind(wx.EVT_BUTTON, self.OnToggleAuto)

    # layout buttons
    button_sizer.Add(self.prev_button, 0, wx.ALL, 1)
    button_sizer.Add(self.next_button, 0, wx.ALL, 1)
    button_sizer.AddStretchSpacer()
    button_sizer.Add(self.auto_button, 0, wx.ALL, 5)
    button_panel.SetSizer(button_sizer)

    # layout main frame
    main_sizer.Add(progress_panel, 1, wx.ALL|wx.EXPAND, 5)
    main_sizer.Add(button_panel, 0, wx.ALL|wx.EXPAND, 5)
    self.SetSizerAndFit(main_sizer)
    self.SetMinSize(size)

    # start Coot
    coot_path = os.environ.get('COOT_PREFIX','')
    coot_cmd = 'bin/coot --no-guano --script %s' %\
               os.path.join(libtbx.env.build_path.sh_value(),
                            '../modules/gui_demo/Coot.py')
    coot_cmd = [os.path.join(coot_path, coot_cmd)]
    self.coot = xmlrpc_utils.external_program_server(
      command_args=coot_cmd, program_id='Coot', timeout=250)

  def update_view(self, prefix):
    if (prefix is not None):
      self.file_text.SetLabel(os.path.basename(prefix))
      f = open(prefix + '.json', 'r')
      table = json.load(f)
      f.close()
      self.t1.update_values(table['Table 1'])
      self.Layout()

      model_file = prefix + '.pdb'
      mtz_file = prefix + '.mtz'
      if (self.coot.is_alive()):
        self.coot.update_model(model_file)
        self.coot.close_maps()
        self.coot.auto_load_maps(mtz_file)

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
