#!/usr/local/bin/python3

import argparse
import logging

from elasticsearch import Elasticsearch, helpers


def get_args():
    parser = argparse.ArgumentParser(
        description="Remove duplicates from an Elasticsearch index."
    )
    parser.add_argument(
        "-e",
        "--es-host",
        type=str,
        default="http://localhost:9200",
        help="Elasticsearch host (default: http://localhost:9200)",
    )
    parser.add_argument(
        "-i",
        "--index-name",
        type=str,
        required=True,
        help="Name of the Elasticsearch index",
    )
    parser.add_argument(
        "-k",
        "--keys",
        type=str,
        required=True,
        help="Comma-separated list of fields to use for determining duplicates",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="INFO",
        help="Logging level (default: INFO)",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser.parse_args()


def scroll_over_all_docs(es, index_name: str, keys_to_include_in_hash: list[str]):
    dict_of_duplicate_docs = {}
    count = 0
    for hit in helpers.scan(es, index=index_name):
        combined_key = tuple([hit["_source"][key] for key in keys_to_include_in_hash])
        dict_of_duplicate_docs.setdefault(combined_key, []).append(hit["_id"])
        count += 1
    return dict_of_duplicate_docs, count


def loop_over_hashes_and_remove_duplicates(
    es, index_name: str, dict_of_duplicate_docs: dict[tuple, list]
):
    for key, array_of_ids in dict_of_duplicate_docs.items():
        if len(array_of_ids) > 1:
            logging.info("Delete duplicate docs with key=%s", key)
            for doc_id in array_of_ids:
                es.delete(index=index_name, id=doc_id)


def main():
    args = get_args()
    es = Elasticsearch([args.es_host])
    keys_to_include_in_hash = args.keys.split(",")
    dict_of_duplicate_docs, docs_count = scroll_over_all_docs(
        es, args.index_name, keys_to_include_in_hash
    )
    not_duplicated_count = len(dict_of_duplicate_docs)

    logging.basicConfig(level=args.log_level, format="%(message)s")

    loop_over_hashes_and_remove_duplicates(es, args.index_name, dict_of_duplicate_docs)
    logging.info("Number of docs before deduplication: %d", docs_count)
    logging.info("Number of docs after deduplication: %d", not_duplicated_count)


if __name__ == "__main__":
    main()
