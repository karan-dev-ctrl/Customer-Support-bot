select
    'bitext-' || cast(message_id as varchar) as message_id,
    'bitext'                                 as source_dataset,
    text,
    intent,
    category,
    cast(null as varchar)                    as emotions,
    reference_response
from {{ ref('stg_bitext') }}

union all

select
    'goemotions-' || cast(message_id as varchar),
    'goemotions',
    text,
    cast(null as varchar),
    cast(null as varchar),
    emotions,
    cast(null as varchar)
from {{ ref('stg_goemotions') }}