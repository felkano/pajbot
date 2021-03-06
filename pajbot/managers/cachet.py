import logging
import time
import json

import cachetclient.cachet as cachet

log = logging.getLogger(__name__)


class CachetManager:
    def __init__(self, bot):
        self.bot = bot
        self.metrics = {}

        self.messages_processed = []
        self.metric_message_processing_time = None

        if 'cachet' in bot.config:
            bot.execute_every(10, self._post_metrics)

            self.endpoint = bot.config['cachet']['endpoint']
            self.api_token = bot.config['cachet']['api_token']

            self.metric_message_processing_time = bot.config['cachet']['metric_message_processing_time']
            self.metric_messages_processed = bot.config['cachet']['metric_messages_processed']

            ping = cachet.Ping(endpoint=self.endpoint)
            print(ping.get())

    def _post_metrics(self):
        log.debug('Posting metrics')
        points = cachet.Points(endpoint=self.endpoint, api_token=self.api_token)

        if len(self.messages_processed) > 0:
            if self.metric_message_processing_time:
                avg_mpt = sum(self.messages_processed)/len(self.messages_processed)
                xd = points.post(id=self.metric_message_processing_time, value=avg_mpt)
                log.debug(json.loads(xd))

            if self.metric_messages_processed:
                xd = points.post(id=self.metric_messages_processed, value=len(self.messages_processed))
                log.debug(json.loads(xd))

            self.messages_processed = []

    def add_message_processing_time(self, process_time):
        self.messages_processed.append(process_time)

class MPTMetric:
    def __init__(self, cm):
        self.cm = cm

    def __enter__(self):
        self._t1 = time.time()
        return None

    def __exit__(self, type, value, traceback):
        self._t2 = time.time()

        self.cm.add_message_processing_time(self._t2-self._t1)
