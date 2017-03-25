# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys
import os
from credentials import TOKEN
from webapp2 import WSGIApplication, Route
from request_handling.request_handlers import IndexHandler, AddBotHandler, DeleteBotHandler

sys.path.append(os.path.join(os.path.abspath('.'), 'venv/Lib/site-packages'))

webapp2_config = {}
webapp2_config['webapp2_extras.sessions'] = {
    'secret_key': 'Im_an_alien',
}

routes = [
    ('/', IndexHandler),

    # Routes for admin panel
    Route('/set_webhook/<token>', handler='request_handling.request_handlers.WebHookOperationsHandler:set_webhook'),
    Route('/unset_webhook/<token>', handler='request_handling.request_handlers.WebHookHandler:unset_webhook'),
    ('/addbot', AddBotHandler),
    ('/deletebot', DeleteBotHandler),

    # Route for Telegram updates
    Route('/bot_handler/<token>', handler='request_handling.request_handlers.WebHookHandler:webhook_handler')

]

app = WSGIApplication(routes, config=webapp2_config, debug=False)
