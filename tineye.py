import httplib
import mimetypes

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

