select
    id          as message_id,
    trim(text)  as text,
    emotions,
    split
from {{ source('raw', 'goemotions') }}
where text is not null and trim(text) <> ''