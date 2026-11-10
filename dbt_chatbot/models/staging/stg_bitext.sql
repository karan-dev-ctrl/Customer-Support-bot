select
    row_number() over ()   as message_id,
    trim(instruction)      as text,
    lower(category)        as category,
    lower(intent)          as intent,
    response               as reference_response
from {{ source('raw', 'bitext') }}
where instruction is not null and trim(instruction) <> ''