ATTACH TABLE _ UUID 'd5d97569-2c97-4b32-ac05-feacfa234ca2'
(
    `sentiment_score` Int32,
    `count` UInt64
)
ENGINE = MergeTree
ORDER BY sentiment_score
SETTINGS index_granularity = 8192
