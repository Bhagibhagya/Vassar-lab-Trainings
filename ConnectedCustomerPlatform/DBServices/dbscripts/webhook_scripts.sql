CREATE SCHEMA IF NOT EXISTS webhook;

SET search_path TO webhook;


CREATE TABLE IF NOT EXISTS microsoft_notification
(
    notification_uuid VARCHAR(45) PRIMARY KEY,
    notification_json JSONB
);
