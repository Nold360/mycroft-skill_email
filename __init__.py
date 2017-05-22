# Copyright (c) 2017 Gerrit 'Nold' Pannek 
# https://nold.in
#
# This Mycroft Skill is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.

import imaplib
import email
import email.header

from os.path import dirname
from time import sleep

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'nold'

logger = getLogger(__name__)

class EmailSkill(MycroftSkill):
    imap_server = None
    imap_port = 993
    imap_username = None
    imap_password = None
    imap_inbox = 'INBOX'

    def __init__(self):
        super(EmailSkill, self).__init__(name="EmailSkill")

    def initialize(self):
        self.load_data_files(dirname(__file__))
        if self.config:
            self.imap_server = self.config.get('server', None)
            self.imap_port = self.config.get('port', 993)
            self.imap_username = self.config.get('username', None)
            self.imap_password = self.config.get('password', None)
            self.imap_inbox = self.config.get('inbox', 'inbox')
        else:
            logger.warn("You havn't configured EmailSkill!")

        intent = IntentBuilder("CheckEmails").require("CheckMyEmails").build()
        self.register_intent(intent, self.handle_check_emails)

    def stop(self):
        pass

    def handle_check_emails(self, message):
        if (self.imap_server != None) \
            and (self.imap_username != None) \
            and (self.imap_password != None):
            conn = imaplib.IMAP4_SSL(self.imap_server)
            try:
                rv, data = conn.login(self.imap_username, self.imap_password)
            except imaplib.IMAP4.error:
                logger.warn("ERROR: Couldn't login to your E-Mail account: " + self.imap_user + '@' + self.imap_server)
                self.speak("Sorry, I couldn't login to your E-Mail account!")

        if rv == 'OK':
            conn.select(self.imap_inbox)
            conn.select(readonly=1)
            (rv, messages) = conn.search(None, '(UNSEEN)')
            if rv == 'OK':
                count = 0
                for num in messages[0].split(' '):
                    count += 1

                if count == 1:
                    self.speak("You have %s new message!" % str(count))
                else:
                    self.speak("You have %s new messages!" % str(count))
                    
                count = 0
                for num in messages[0].split(' '):
                    count += 1
                    typ, data = conn.fetch(num,'(RFC822)')
                    msg = email.message_from_string(data[0][1])
                    decode = email.header.decode_header(msg['Subject'])[0]
                    subject = unicode(decode[0])
                    self.speak("Message %s: %s" % (str(count), subject))
                    sleep(1)

def create_skill():
    return EmailSkill()
