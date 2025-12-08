"""Common utilities for spark-streaming jobs.

This module centralizes small helpers used by both silver and gold jobs:
- configure_s3a(spark, minio_conf)
- load_config(path)
- build_checkpoint_path(base, topic)

Keep these functions small and dependency-free so scripts can import them
easily in local and containerized runs.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def configure_s3a(spark, minio_conf: Optional[Dict[str, Any]]) -> None:
    """Configure Hadoop S3A settings on the Spark context using a MinIO-like config.

    minio_conf is expected to be a dict with optional keys:
      - endpoint (e.g. "http://minio:9000")
      - access_key
      - secret_key

    This is a no-op when minio_conf is falsy.
    """
    if not minio_conf:
        return

    endpoint = minio_conf.get("endpoint")
    access = minio_conf.get("access_key")
    secret = minio_conf.get("secret_key")
    hconf = spark._jsc.hadoopConfiguration()

    if endpoint:
        # Hadoop expects host[:port] (no schema)
        ep = endpoint.replace("http://", "").replace("https://", "")
        hconf.set("fs.s3a.endpoint", ep)

    if access:
        hconf.set("fs.s3a.access.key", access)

    if secret:
        hconf.set("fs.s3a.secret.key", secret)

    # Common settings for MinIO/S3A
    hconf.set("fs.s3a.path.style.access", "true")

    # If endpoint explicitly uses http, disable ssl in the S3A connector
    if endpoint and endpoint.startswith("http://"):
        hconf.set("fs.s3a.connection.ssl.enabled", "false")


def load_config(path: str) -> Dict[str, Any]:
    """Load a JSON configuration file from disk and return its dictionary.

    Raises FileNotFoundError or json.JSONDecodeError for invalid files.
    """
    if not path:
        raise ValueError("config path must be provided")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_checkpoint_path(base: str, topic: Optional[str]) -> str:
    """Build a checkpoint path by joining base and topic.

    This helper normalizes trailing slashes and performs a simple heuristic
    check to warn if the resulting path doesn't look like durable storage
    (for example, local '/tmp' paths). It does not enforce any policy, but
    prints a warning to help avoid accidental local checkpointing in prod.

    Example return values:
      - "s3a://silver/topics/orders/checkpoint"
      - "s3a://silver/topics/order_details/checkpoint"
    """
    if not base:
        raise ValueError("checkpoint base path must be provided")

    # normalize
    base_norm = base.rstrip("/")
    topic_norm = (topic or "").strip("/")

    if topic_norm:
        ckpt = f"{base_norm}/{topic_norm}/checkpoint"
    else:
        ckpt = f"{base_norm}/checkpoint"

    # simple heuristic: prefer durable stores (s3a, s3, hdfs)
    if not (ckpt.startswith("s3a://") or ckpt.startswith("s3://") or ckpt.startswith("hdfs://")):
        print(f"[WARN] checkpoint path '{ckpt}' does not look like durable storage (s3a:// or hdfs://).")

    return ckpt
