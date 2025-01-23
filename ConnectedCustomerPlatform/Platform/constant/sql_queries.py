get_llm_configurations_by_customer_uuid_query= """
            SELECT 
                llm_configuration_name,
                llm_configuration_uuid,
                CAST((llm_configuration_details_json::jsonb - 'api_key')AS JSON) AS llm_configuration_details_json,                customer_uuid,
                llm_provider_uuid,
                customer_uuid,
                created_by,
                updated_by
            FROM 
                llm_configuration
            WHERE 
                is_deleted = FALSE 
                AND customer_uuid = '{0}'
            ORDER BY 
                inserted_ts DESC;
            """

get_llm_configuration_by_llm_config_uuid="""
            SELECT 
                llm_configuration_name,
                llm_configuration_uuid,
                CAST((llm_configuration_details_json::jsonb - 'api_key')AS JSON) AS llm_configuration_details_json,
                llm_provider_uuid,
                customer_uuid,
                created_by,
                updated_by
            FROM 
                llm_configuration
            WHERE 
                is_deleted = FALSE 
                AND llm_configuration_uuid = '{0}'
            ORDER BY 
                inserted_ts DESC;
            """