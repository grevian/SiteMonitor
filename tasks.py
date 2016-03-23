import logging

from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.ext import ndb

from models import SiteStatus, SiteCheck


def check_sites(site_configurations):

    # Query all the sites we've been given to check
    request_rpc_futures = []
    for site in site_configurations:
        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, site.target)
        request_rpc_futures.append((site, rpc,))

    # Process the results and write out the status update
    status_futures = []
    for site, rpc in site_configurations:
        status = SiteCheck(
                parent=site.key(),
                status=SiteStatus.ONLINE
        )

        try:
            result = rpc.get_result()

            if result.status_code != 200:
                status.status = SiteStatus.ERROR

            if result.content != "":
                status.status = SiteStatus.UNEXPECTED

        except urlfetch.DownloadError:
            status.status = SiteStatus.OFFLINE

        if not SiteStatus.available(status.status):
            pass  # TODO Send an alert if required

        status_futures.append(status.put_async())

    ndb.Future.wait_all(status_futures)


def send_failure_notification(site, status):
    for monitor in site.monitors:
        if not monitor.enabled:
            continue

        AlertSent(
            parent=site.key(),
            failed_check=status,

        )
        msg = "%s failed a status check at %s, the status recorded was %s" % (site.name,
                                                                              status.check_time,
                                                                              status.status)
        if monitor.method in ("EMAIL", "BOTH",):
            logging.warn(msg)
            mail.send_mail("anything@grevian-site-monitor.appspotmail.com",
                           monitor.email,
                           "Failure Notification: %s" % site.name,
                           msg)

        if monitor.method in ("SMS", "BOTH",):
            pass  # TODO Send an SMS with the twilio api
