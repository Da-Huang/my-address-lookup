#coding: utf8

import webapp2, logging
from google.appengine.ext import db

PAGE_TEMPLATE = """\
<html><body>
<h1>達さんの%sは<a href=//%s>%s</a>です。</h1>
</body></html>
"""
ERROR_PAGE_TEMPLATE = """\
<html><body>
<h1>%s</h1>
</body></html>
"""

class Fetch(webapp2.RequestHandler):
  def get(self):
    address_query = Address.all()
    addresses = address_query.fetch(1)
    logging.info(('addr:', addresses))
    if addresses:
      ip = addresses[0].ip
      if ip:
        ip = ip.encode('utf8')
        if ':' in ip:
          url = '[%s]' % ip
          ip_type = 'IPv6'
        else:
          url = ip
          ip_type = 'IP'
        self.response.write(PAGE_TEMPLATE % (ip_type, url, ip))
      else:
        self.response.write(ERROR_PAGE_TEMPLATE % 'ここに達さんのIPがありません。')
    else:
      self.response.write(ERROR_PAGE_TEMPLATE % 'o(╯□╰)o データ エラー')

class Address(db.Model):
  secret_token = db.StringProperty()
  ip = db.StringProperty()
  def __str__(self):
    return 'ip=%s,secret_token=%s' % (self.ip, self.secret_token)
  def __repr__(self):
    return self.__str__()

class Store(webapp2.RequestHandler):
  def get(self):
    secret_token = self.request.get('secret_token')
    logging.info(('secret_token:', secret_token))
    if not secret_token or not isinstance(secret_token, unicode):
      self.response.write(ERROR_PAGE_TEMPLATE % '失敗です。')
      return;
    address_query = Address.gql("WHERE secret_token=:secret_token", secret_token=secret_token)
    addresses = address_query.fetch(1)
    logging.info(('store:', addresses))
    if addresses:
      addresses[0].ip = self.request.remote_addr
      db.put(addresses)
      self.response.write(ERROR_PAGE_TEMPLATE % '成功です。')
    else:
      self.response.write(ERROR_PAGE_TEMPLATE % '失敗です。')

if not Address().all().fetch(1): Address(ip='', secret_token='').put()
application = webapp2.WSGIApplication([
  ('/', Fetch),
  ('/store', Store),
], debug=False)

