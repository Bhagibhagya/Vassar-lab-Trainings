

get_question_details_query = """SELECT q.question_uuid, q.question, a.answer_uuid, a.answer, a.attachment_details_json, d.draft_uuid,
                           d.draft, d.attachment_details_json AS draft_attachments, a.is_verified, a.feedback,
                           MAX(
                                CASE
                                    WHEN rram.resource_action_id = %s THEN 1
                                    ELSE 0
                                END) AS sme_verified,
                           MAX(
                                CASE
                                    WHEN rram.resource_action_id = %s THEN 1
                                    ELSE 0
                                END) AS qa_verified,
                            jsonb_agg(jsonb_build_object('entity_uuid', e.entity_uuid, 'entity_name', e.entity_name)) AS entity_info_json
                           FROM questions q
                             JOIN answers a ON q.answer_uuid = a.answer_uuid
                             LEFT JOIN drafts d ON a.answer_uuid = d.answer_uuid
                             LEFT JOIN LATERAL ( SELECT e_1.entity_uuid,
                                    e_1.entity_name
                                   FROM entities e_1
                                  WHERE (e_1.entity_uuid::text IN ( SELECT *
                                           FROM jsonb_array_elements_text(a.entity_details_json)))) e ON true
                             LEFT JOIN usermgmt.role_resource_action_mapping rram
                                ON rram.role_id = a.verifier_role_uuid AND rram.resource_action_id IN (%s, %s)
                        
                        where q.question_uuid = %s::text
                        """