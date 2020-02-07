LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "%(levelname)s %(message)s"
        }
    },
    "handlers": {
        "cloudwatch": {
            "class": "botoless.logging.CloudwatchQueueHandler",
            "formatter": "standard",
            "group_name": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["cloudwatch"],
        "propagate": "yes"
    }
}
