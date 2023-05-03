import elastic_transport
from elasticsearch import Elasticsearch, helpers
import time
import math


class Pipeline:
    def __init__(
        self, index_name, mapping, es_host, es_port, es_user, es_pass, bulk_size=1000
    ):
        self.mapping = mapping

        self.index_name = index_name
        self.elastic_host = es_host + ":" + str(es_port)

        self.es = Elasticsearch(
            self.elastic_host,
            basic_auth=[
                es_user,
                es_pass,
            ],
            timeout=10,
        )

        if not self.es.indices.exists(index=self.index_name):
            print("Creating index: " + self.index_name)
            self.es.indices.create(index=self.index_name, body=self.mapping)

        self.doc_queue = []
        self.queue_max = bulk_size

    def close_queue(self):
        try:
            print("Indexing remaining documents in queue.")
            helpers.bulk(self.es, self.doc_queue, index=self.index_name)
        except elastic_transport.ConnectionTimeout:
            self.handle_timeout()
        except Exception as e:
            print(e)
        self.doc_queue = []
        return

    def ingest_json(self, json_payload):
        self.doc_queue.append(json_payload)

        if len(self.doc_queue) > self.queue_max:
            try:
                print("Indexing " + str(len(self.doc_queue)) + " documents.")
                helpers.bulk(self.es, self.doc_queue, index=self.index_name)
                self.doc_queue = []
            except elastic_transport.ConnectionTimeout:
                self.handle_timeout()
            except Exception as e:
                print(e)
                self.close_queue()

    def handle_timeout(self):
        print("Indexing resulted in timeout! Retrying...")
        processed = False
        attempts = 0
        backoff = 1
        max_backoff = 64
        while not processed:
            try:
                helpers.bulk(self.es, self.doc_queue, index=self.index_name)
                processed = True
            except elastic_transport.ConnectionTimeout:
                print("Indexing resulted in timeout! Retrying...")
                attempts = attempts + 1
                backoff = min(math.pow(2, attempts), max_backoff)
                time.sleep(backoff)
