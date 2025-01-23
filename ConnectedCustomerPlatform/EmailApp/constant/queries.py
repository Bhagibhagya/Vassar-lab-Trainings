QUERY_FOR_FETCHING_INTENTS_SUBINTENTS = """
    SELECT 
        intent_dim.dimension_name AS intent_name,
        ARRAY_AGG(subintent_dim.dimension_name) AS sub_intent_names
    FROM 
        dimension_customer_application_mapping AS intent_mapping
    JOIN 
        dimension AS intent_dim ON intent_mapping.dimension_uuid = intent_dim.dimension_uuid
    JOIN 
        dimension_type AS intent_dim_type ON intent_dim.dimension_type_uuid = intent_dim_type.dimension_type_uuid
    LEFT JOIN 
        dimension_customer_application_mapping AS subintent_mapping ON intent_mapping.dimension_uuid = subintent_mapping.parent_dimension_uuid
    LEFT JOIN 
        dimension AS subintent_dim ON subintent_mapping.dimension_uuid = subintent_dim.dimension_uuid
    LEFT JOIN 
        dimension_type AS subintent_dim_type ON subintent_dim.dimension_type_uuid = subintent_dim_type.dimension_type_uuid
    WHERE 
        intent_dim_type.dimension_type_name = %s
        AND (subintent_dim_type.dimension_type_name = %s OR subintent_dim_type.dimension_type_name IS NULL)
        AND intent_mapping.customer_uuid = %s
        AND intent_mapping.application_uuid = %s
        AND subintent_mapping.customer_uuid= %s
        AND subintent_mapping.application_uuid= %s
        AND intent_dim.is_deleted = FALSE
        AND intent_dim.status = TRUE
        AND (subintent_dim.is_deleted = FALSE OR subintent_dim.is_deleted IS NULL)
        AND (subintent_dim.status = TRUE OR subintent_dim.status IS NULL)
    GROUP BY 
        intent_dim.dimension_name
    ORDER BY 
        intent_dim.dimension_name;
"""