import logging
from smtplib import SMTP, SMTPSenderRefused

import pytest
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink

from bebleo_smtpd_fixture.smtp import AuthSMTP

log = logging.getLogger(__name__)


@pytest.fixture
def no_auth(request):
    class PseudoController(Controller):
        def factory(self):
            return AuthSMTP(self.handler)

    controller = PseudoController(Sink(), hostname="127.0.0.1", port="8025")
    request.addfinalizer(controller.stop)
    controller.start()
    return controller


def test_missing_auth_handler(no_auth):
    with SMTP(no_auth.hostname, no_auth.port) as client:
        code, resp = client.docmd('AUTH', "PSEUDOMECH")
        assert code == 502


def test_use_starttls(mock_smtpd_use_starttls, smtpd, msg):
    with SMTP(smtpd.hostname, smtpd.port) as client:
        with pytest.raises(SMTPSenderRefused):
            code, resp = client.send_message(msg)