#!/usr/bin/env python

import httplib
import mimetypes
import nautilus
import os
import logging
import subprocess

using_gtk = True

try:
  import pygtk
  pygtk.require("2.0")
  import gtk
except ImportError:
  using_gtk = False

BOUNDARY="---------------------------46798320320190039671482364942"

def post_multipart(host, selector, fields, files):
  # Adapted from http://code.activestate.com/recipes/146306-http-client-to-post-using-multipartform-data/
  content_type, body = encode_multipart_formdata(fields, files)
  h = httplib.HTTP(host)
  h.putrequest('POST', selector)
  h.putheader('host', host)
  h.putheader('referer', 'http://www.tineye.com/')
  h.putheader('User-Agent: nautilus-tineye-plugin')
  h.putheader('content-type', content_type)
  h.putheader('content-length', str(len(body)))
  h.endheaders()
  h.send(body)
  errcode, errmsg, headers = h.getreply()
  return headers.__str__()

def encode_multipart_formdata(fields, files):
  CRLF = '\r\n'
  L = []
  for (key, value) in fields:
    L.append("--" + BOUNDARY)
    L.append('Content-Disposition: form-data; name="%s"' % key)
    L.append('')
    L.append(value)
  for (key, filename, value) in files:
    L.append("--" + BOUNDARY)
    L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
    L.append('Content-Type: %s' % get_content_type(filename))
    L.append('')
    L.append(value)
  L.append(BOUNDARY + "--")
  L.append('')
  body = CRLF.join(L)
  content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
  return content_type, body

def get_content_type(filename):
  return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

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

    headers = post_multipart("www.tineye.com", "/search", [],
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

