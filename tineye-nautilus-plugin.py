#!/usr/bin/env python
import nautilus
import os
import logging
import subprocess
import tineye

using_gtk = True

try:
  import pygtk
  pygtk.require("2.0")
  import gtk
except ImportError:
  using_gtk = False

def get_executable_filename(name):
  path = "%s/%s" % (os.getcwd(), name)
  if os.path.exists(path) and os.access(path, os.X_OK): return path
  path = "/usr/local/bin/" + name
  if os.path.exists(path) and os.access(path, os.X_OK): return path
  path = "/usr/bin/" + name
  if os.path.exists(path) and os.access(path, os.X_OK): return path
  raise PathNotFound("%s not found" % name)

class TineyePlugin(nautilus.MenuProvider):
  def __init__(self):
      self.extensions = [".gif", ".jpg", ".jpeg", ".png"]

  def get_search_url(self, filename):
    with open(filename) as f:
        data = f.read()

    headers = tineye.post_multipart("www.tineye.com", "/search", [],
                          [("image", filename[filename.rfind("/")+1:], data)])

    for x in headers.split("\n"):
      if x.startswith("Location:"):
        loc, sep, url = x.partition("Location:")
        return url.strip()
    return ""

  def menu_activate_cb(self, menu, filename):

    url = self.get_search_url(filename)

    if not url:
      if using_gtk:
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
          gtk.BUTTONS_OK, "Error. No URL retrieved from Tineye. Please submit manually.")
        dialog.run()
        dialog.destroy()
      return

    path = get_executable_filename("xdg-open")

    subprocess.call([path, url])

  def get_file_items(self, window, files):
    if len(files) != 1:
      return

    filename = files[0].get_uri()
    if filename.startswith("file://"):
      filename = filename[7:]

    ext = os.path.splitext(filename)[1]
    if not ext in self.extensions:
      return

    item = nautilus.MenuItem(
      "TineyePlugin::SubmitAndOpen",
      "Search in Tineye",
      "Search in Tineye"
    )
    item.connect('activate', self.menu_activate_cb, filename)
    
    return [item]

