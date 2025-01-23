CREATE TABLE IF NOT EXISTS dimension_types (
    dimension_type_uuid VARCHAR(45) PRIMARY KEY,
    dimension_type_name VARCHAR(255) NOT NULL, -- Geography,Intent,Sentiment,Customer Tier,State(parent Geography)
    dimension_type_details_json JSONB,
    parent_dimension_type_uuid VARCHAR(45),
    channel_type_uuid VARCHAR(45), -- is it required, depending on the channel type dimension will change or not ?????
    application_uuid VARCHAR(45),
    customer_uuid VARCHAR(45),
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE (dimension_type_name, customer_uuid, application_uuid)
);

ALTER TABLE dimension_types DROP CONSTRAINT dimension_types_dimension_type_name_customer_uuid_key;

CREATE TABLE IF NOT EXISTS dimensions (
    dimension_uuid VARCHAR(45) PRIMARY KEY,
    dimension_name VARCHAR(255) NOT NULL,
    dimension_type_uuid VARCHAR(45) NOT NULL,
    dimension_details_json JSONB,
    parent_dimension_uuid VARCHAR(45), -- Parent dimension UUID
    channel_type_uuid VARCHAR(45), -- is it required, depending on the channel type dimension will change or not ?????
    application_uuid VARCHAR(45),
    customer_uuid VARCHAR(45),
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

ALTER TABLE dimensions ADD FOREIGN KEY (dimension_type_uuid) REFERENCES dimension_types(dimension_type_uuid) ON DELETE CASCADE;
ALTER TABLE dimensions ADD FOREIGN KEY (parent_dimension_uuid) REFERENCES dimensions(dimension_uuid) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS action_flows (
    action_flow_uuid VARCHAR(45) PRIMARY KEY,
    action_flow_name VARCHAR(255) NOT NULL,
    channel_type_uuid VARCHAR(45), -- depending on the channel type actions will change
    application_uuid VARCHAR(45) NOT NULL,
    dimension_details_json JSONB, -- list of dimension configurations
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS customer_clients (
    customer_client_uuid VARCHAR(45) PRIMARY KEY,
    customer_client_geography_uuid VARCHAR(45),--Geography UUID??? for which channel I need to assign
    customer_client_domain_name VARCHAR(255) ,
    customer_client_name VARCHAR(255) NOT NULL,
    customer_client_tier_uuid VARCHAR(45), --Customer Tier  UUID
    customer_uuid VARCHAR(45) NOT NULL,
    customer_client_details_json JSONB, -- Will store the List of CC and BCC information of customer,add the address
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

ALTER TABLE customer_clients ADD FOREIGN KEY (customer_client_geography_uuid) REFERENCES dimensions(dimension_uuid) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS client_users (
    client_user_uuid VARCHAR(45) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255)  NOT NULL,
    email_id VARCHAR(255) NOT NULL UNIQUE,
    dimension_uuid VARCHAR(45) NOT NULL,  -- Geography Id
    customer_client_uuid VARCHAR(45),
    info_json JSONB, -- add required information
    status BOOLEAN DEFAULT TRUE, -- TRUE means user active. False - Inactive/Disabled
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

ALTER TABLE client_users ADD FOREIGN KEY (dimension_uuid) REFERENCES dimensions(dimension_uuid) ON DELETE CASCADE;
ALTER TABLE client_users ADD FOREIGN KEY (customer_client_uuid) REFERENCES customer_clients(customer_client_uuid) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS prompt (
    prompt_uuid VARCHAR(45) PRIMARY KEY,
    prompt_name VARCHAR(255) NOT NULL,
    prompt_category VARCHAR(255) NOT NULL, -- Classification / Intent
    prompt_details_json JSONB, -- will store the response format also,is_base prompt,template uuid
    prompt_dimension_details_json JSONB, --will store the list of Geography,Intent,Sentiment,customer Tier details information, Action flow details and Prompt/Prompt chain
    customer_uuid VARCHAR(45),
    channel_type_uuid VARCHAR(45),
    application_uuid VARCHAR(45) NOT NULL,
    status  BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS prompt_template (
    prompt_template_uuid VARCHAR(45) PRIMARY KEY,
    prompt_template_name VARCHAR(255) NOT NULL,
    prompt_template_details_json JSONB,
    channel_type_uuid VARCHAR(45),
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45),
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE (prompt_template_name, customer_uuid)
);

ALTER TABLE prompt_template DROP CONSTRAINT prompt_template_prompt_template_name_customer_uuid_key;

CREATE TABLE IF NOT EXISTS emails (
    email_uuid VARCHAR(45) PRIMARY KEY,
    customer_uuid VARCHAR(45) NOT NULL,
    customer_client_uuid VARCHAR(45),
    email_task_status VARCHAR(255) NOT NULL, -- Pending,In-progress,Completed,Open,Draft,Sent
    email_action_flow_status VARCHAR(255),
    email_activity JSONB, -- activity log
    email_process_details JSONB, -- details of step will be stored here
    dimension_uuid VARCHAR(45),  -- Intent uuid
    assigned_to VARCHAR(45), --user id of the CSR
    role_uuid VARCHAR(45), --OverAllCSRManager/CSR Manager/CSR
    application_uuid VARCHAR(45),
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

ALTER TABLE emails ADD FOREIGN KEY (customer_client_uuid) REFERENCES customer_clients(customer_client_uuid) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS email_conversations (
    conversation_uuid character varying(100) PRIMARY KEY,
    email_uuid VARCHAR(45) NOT NULL,
    email_subject VARCHAR(255),
    email_flow_status VARCHAR(255),-- AI automated
    email_status VARCHAR(255) NOT NULL, -- Draft,Sent
    email_info_json JSONB, -- (FROM,TO,CC,BCC recipients_details) & email_body_url in S3 & (List of email_attachment_urls in S3) & email meta data & email body summary
    dimension_action_json JSONB, -- Geography,Intent,Sentiment,customer Tier details information, and Action flow details
    parent_uuid VARCHAR(100),
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

ALTER TABLE email_conversations ADD FOREIGN KEY (email_uuid) REFERENCES emails(email_uuid) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS email_server(
    email_server_uuid  VARCHAR(45) PRIMARY KEY,
    server_type VARCHAR(255) NOT NULL,
    server_url VARCHAR(255) NOT NULL,
    email_provider_name VARCHAR(255) NOT NULL,
    port VARCHAR(45) NOT NULL,
    is_ssl_enabled BOOLEAN DEFAULT TRUE,
    sync_time_interval BIGINT DEFAULT 5,
    customer_uuid VARCHAR(45),
    application_uuid VARCHAR(45),
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS user_email_settings(
    user_email_uuid  VARCHAR(45) PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL UNIQUE, -- email
    password_hash VARCHAR(255) NOT NULL,
    email_type VARCHAR(255) NOT NULL,
    email_details_json JSONB,
    is_primary_sender_address BOOLEAN DEFAULT FALSE,
    customer_uuid VARCHAR(45) NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_ts TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- chatbot configurations
CREATE TABLE IF NOT EXISTS chat_configuration(
    chat_configuration_uuid VARCHAR(45) PRIMARY KEY,
    chat_configuration_name VARCHAR(255) NOT NULL,
    description TEXT,
    chat_details_json JSONB,--CSS template Details & details Json
    code TEXT,
    application_uuid VARCHAR(45),
    customer_uuid VARCHAR(45),
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tools(
    tool_uuid VARCHAR(45) PRIMARY KEY,
    tool_description VARCHAR(255),
    tool_name VARCHAR(255),
    is_built_in BOOLEAN DEFAULT TRUE,
    code_details_json JSONB, -- parameters ,methods,parameters type,response type, any code
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45),
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS agent(
    agent_uuid VARCHAR(45) PRIMARY KEY,
    agent_description VARCHAR(255),
    agent_name VARCHAR(255),
    dimension_details_json JSONB,
    agent_details_json JSONB, -- prompt,tools list and any extra information
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45),
    status BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- NO SQL
CREATE TABLE conversations (
    conversation_uuid VARCHAR(45) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_details_json JSONB,--    { //uid: number,name: Name,userType: {AUTHENTICATED,NON_AUTHENTICATED},profilePicture: S3Object},
    conversation_status VARCHAR(100) NOT NULL, -- ONGOING_BOT,UNASSIGNED,ONGOING_AGENT,RESOLVED
    csr_info_json JSONB,  --  { // array because a chat could be escalated between multiple agents, in case the bot completely handles a chat and never triggers a human handoff this array would be empty
                          --     csr uid: number,
                          --     name: Name,
                          --     profilePicture: S3Object
                          --  },
    csr_hand_off BOOLEAN DEFAULT false, -- it is essentially to capture if a humanHandoff was triggered by the bot or not
    conversation_stats_json JSONB, -- eventTiming: EventTiming {conversationStartTime: TIMESTAMP, humanHandoffTime: TIMESTAMP, firstAgentAssignmentTime: TIMESTAMP,firstAgentMessageTime: TIMESTAMP,lastUserMessageTime: TIMESTAMP,lastAgentMessageTime: TIMESTAMP,conversationResolutionTime: TIMESTAMP}
    conversation_feedback_transaction_json JSONB, --  //after the conversation is resolved, user app will request the user to submit the feedback for this particular conversation              	{satisfactionScoreOnTen: number,additionalComments: string  },
    task_details_json JSONB,-- if csr created a task,will store the task details
    summary TEXT NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    message_details_json JSONB,--id VARCHAR(45),user_id VARCHAR(45),--User id & CSR ID,csr_id VARCHAR(45),source  VARCHAR(45),-- bot,csr,user ,message_marker VARCHAR(255), --LOGGED,DELIVERED, READ,    dimension_action_json JSONB,-- dimension & Action will store here,message_text TEXT NOT NULL,media_url VARCHAR(255),parent_message_uuid VARCHAR(45),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- view to fetch tickets for unified activity dashboard ordered by date
CREATE OR REPLACE VIEW unified_activity AS
SELECT
    e.email_uuid AS activity_uuid,
    e.email_action_flow_status AS status,
    e.updated_ts AS timestamp,
    (ec.email_info_json ->> 'sender_name') AS client_name,  -- Handle NULLs
    (ec.email_info_json ->> 'sender') AS email_id,  -- Handle NULLs
    d.dimension_name AS intent,  -- Use JOIN instead of subquery
    'email' AS channel,  -- Specify the channel as 'email'
    e.application_uuid AS application_uuid,
    e.customer_uuid AS customer_uuid
FROM emails e
JOIN email_conversations ec ON e.email_uuid = ec.email_uuid
LEFT JOIN dimensions d ON d.dimension_uuid = e.dimension_uuid  -- Optimized join
WHERE ec.parent_uuid IS NULL
UNION ALL
SELECT
    c.conversation_uuid AS activity_uuid,
    c.conversation_status AS status,
    c.insert_ts AS timestamp,
    (c.user_details_json ->> 'name') AS client_name,  -- Handle NULLs
    (c.user_details_json ->> 'email_id') AS email_id,  -- Handle NULLs
    (c.message_details_json -> -1 -> 'dimension_action_json' ->> 'value') AS intent,  -- Handle NULLs
    'chat' AS channel,  -- Specify the channel as 'chat'
    c.application_uuid AS application_uuid,
    c.customer_uuid AS customer_uuid
FROM conversations c
ORDER BY timestamp DESC;

CREATE TABLE countries (
    id bigint NOT NULL PRIMARY KEY,
    name character varying(100) NOT NULL,
    iso3 character(3),
    numeric_code character(3),
    iso2 character(2),
    phonecode character varying(255),
    capital character varying(255),
    currency character varying(255),
    currency_name character varying(255),
    currency_symbol character varying(255),
    tld character varying(255),
    native character varying(255),
    region character varying(255),
    region_id bigint,
    subregion character varying(255),
    subregion_id bigint,
    nationality character varying(255),
    timezones text,
    translations text,
    latitude numeric(10,8),
    longitude numeric(11,8),
    emoji character varying(191),
    "emojiU" character varying(191),
    created_at timestamp without time zone,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    flag smallint DEFAULT 1 NOT NULL,
    "wikiDataId" character varying(255)
);

CREATE TABLE states (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    country_id bigint NOT NULL,
    country_code character(2) NOT NULL,
    fips_code character varying(255),
    iso2 character varying(255),
    type character varying(191),
    latitude numeric(10,8),
    longitude numeric(11,8),
    created_at timestamp without time zone,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    flag smallint DEFAULT 1 NOT NULL,
    "wikiDataId" character varying(255)
);


ALTER TABLE ONLY public.states
    ADD CONSTRAINT states_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);

CREATE TABLE IF NOT EXISTS workflow (
    workflow_uuid VARCHAR(45) PRIMARY KEY,
    workflow_name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    status BOOLEAN DEFAULT TRUE,
    customer_uuid VARCHAR(45),
    application_uuid VARCHAR(45),
    channel_type_uuid VARCHAR(45),
    workflow_details_json JSONB ,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS step (
    step_uuid VARCHAR(45) PRIMARY KEY,
    workflow_uuid VARCHAR(45) NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    step_details_json JSONB,
    step_type VARCHAR(255),
    notes TEXT,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (workflow_uuid) REFERENCES workflow(workflow_uuid) ON DELETE CASCADE
);

ALTER TABLE customer_clients ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE client_users ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE prompt_template ADD COLUMN prompt_category_uuid VARCHAR(255) NOT NULL;
ALTER TABLE prompt_template ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE dimensions ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE dimension_types ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE prompt ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;

-- This table is used to store prompt categories - metadata table will have only two values, Cla
CREATE TABLE IF NOT EXISTS prompt_category (
    prompt_category_uuid VARCHAR(45) PRIMARY KEY,
    prompt_category_name VARCHAR(255) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

ALTER TABLE chat_configuration ADD COLUMN chat_configuration_type VARCHAR(255) NOT NULL;
ALTER TABLE chat_configuration ADD COLUMN status BOOLEAN DEFAULT FALSE;
ALTER TABLE chat_configuration ADD COLUMN is_default BOOLEAN DEFAULT FALSE;
ALTER TABLE chat_configuration ADD COLUMN chat_configuration_provider VARCHAR(255) NOT NULL;


-- This table is used to store the llm configuration for an organization and application combination
CREATE TABLE IF NOT EXISTS llm_configuration (
    llm_configuration_uuid VARCHAR(45) PRIMARY KEY,
    llm_configuration_name VARCHAR(255) NOT NULL,
    llm_configuration_details_json JSONB, -- API_Key, Deployment_Name, API_Base, Model_Name, API_Type, API_Version
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS llm_provider_meta_data (
    llm_provider_uuid VARCHAR(45) PRIMARY KEY,
    llm_provider_name VARCHAR(255) NOT NULL,
    llm_provider_details_json JSONB,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- This table is used to store the llm configuration mapping with respect to channels for an organization and application combination
CREATE TABLE IF NOT EXISTS llm_configuration_channel_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    llm_configuration_uuid VARCHAR(45) NOT NULL,
    channel_uuid VARCHAR(45) NOT NULL,
    mapping_details_json JSONB,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS customer_client_tier_application_mapping(
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    customer_client_uuid VARCHAR(45) NOT NULL,
    tier_uuid VARCHAR(45) NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    template_details_json JSONB,
    is_deleted BOOLEAN DEFAULT FALSE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (tier_uuid) REFERENCES dimensions(dimension_uuid),
    FOREIGN KEY (customer_client_uuid) REFERENCES customer_clients(customer_client_uuid),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id)
);

-- every application has few entities which are like categories among which files can be segregated
-- every entity can have multiple attributes and each attribute can have multiple values
CREATE TABLE entities (
    entity_uuid VARCHAR(45) PRIMARY KEY,
    entity_name VARCHAR(30) NOT NULL,
    entity_description TEXT,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45),
    attribute_details_json JSONB,    -- all the attributes and attribute values of that entity
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id)
);

-- files table to store the files added to an application
-- knowledge from these files will be extracted and used to answer questions in that application
CREATE TABLE files (
    file_uuid VARCHAR(45) PRIMARY KEY,
    file_name VARCHAR(254) NOT NULL,
    file_path TEXT NOT NULL,
    error_details_json JSONB,    -- store error uuids, error types, error statuses
    file_metadata JSONB,    -- store no. of pages, language, no. of web pages scraped, video length
    file_status VARCHAR(64) NOT NULL,
    file_type VARCHAR(30) NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45),
    entity_uuid VARCHAR(45) NOT NULL,
    image_map JSONB,    -- the mapping of image names and their azure blob urls
    attribute_details_json JSONB,    -- attributes and attribute values assigned to the file
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (entity_uuid) REFERENCES entities(entity_uuid),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id)
);

-- answers table contains the answers along with attachment urls to questions asked in an application
-- answers can also be edited, verified, new drafts can be saved and can be upgraded to answers
CREATE TABLE answers (
    answer_uuid VARCHAR(45) PRIMARY KEY,
    answer TEXT,
    attachment_details_json JSONB,    -- store the azure blob urls of images, videos and video timestamps
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45),
    draft JSONB,    -- the drafted answers along with active statuses, user_uuids and user_roles of the sme/qa who made the drafts
    feedback TEXT,
    verification_details_json JSONB,    -- verification status (verified by qa/verified by sme) and user_uuid and user_roles of the verifiers
    author_details_json JSONB,    -- store info whether the answer is system generated or sme/qa generated along with their roles and uuids
    file_details_json JSONB,    -- store the file_names and file_uuids from which answer has been generated
    entity_details_json JSONB,    -- store the entity_names and entity_uuids about which the answer is concerned about
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id)
);

-- the questions that have been asked or generated from the knowledge in an application
CREATE TABLE questions (
    question_uuid VARCHAR(45) PRIMARY KEY,
    question TEXT,
    answer_uuid VARCHAR(45) NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45),
    author_details_json JSONB,    -- store info whether question is user asked or system generated and user_uuid of the user who asked the question
    in_cache BOOLEAN DEFAULT TRUE,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY(answer_uuid) REFERENCES answers(answer_uuid),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id)
);

-- Foreign key constraints
ALTER TABLE dimension_types ADD CONSTRAINT fk_dimension_types_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE prompt_template ADD CONSTRAINT fk_prompt_template_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE email_server ADD CONSTRAINT fk_email_server_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE workflow ADD CONSTRAINT fk_workflow_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE customer_client_tier_application_mapping
DROP CONSTRAINT customer_client_tier_application_mapping_application_uuid_fkey;

ALTER TABLE customer_client_tier_application_mapping ADD CONSTRAINT fk_customer_client_tier_application_mapping_application_uuid
FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE action_flows ADD CONSTRAINT fk_action_flows_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE chat_configuration ADD CONSTRAINT fk_chat_configuration_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE prompt ADD CONSTRAINT fk_prompt_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE emails ADD CONSTRAINT fk_emails_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE user_email_settings ADD CONSTRAINT fk_user_email_settings_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE dimensions ADD CONSTRAINT fk_dimensions_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE tools ADD CONSTRAINT fk_tools_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE agent ADD CONSTRAINT fk_agent_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE conversations ADD CONSTRAINT fk_conversations_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE entities DROP CONSTRAINT entities_application_uuid_fkey;

ALTER TABLE files DROP CONSTRAINT files_application_uuid_fkey;

ALTER TABLE questions DROP CONSTRAINT questions_application_uuid_fkey;

ALTER TABLE answers DROP CONSTRAINT answers_application_uuid_fkey;

ALTER TABLE entities ADD CONSTRAINT fk_entities_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE files ADD CONSTRAINT fk_files_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE answers ADD CONSTRAINT fk_answers_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;

ALTER TABLE questions ADD CONSTRAINT fk_questions_application_uuid FOREIGN KEY (application_uuid)
REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE;


-- Customer uuid foreign key constraint
ALTER TABLE dimension_types ADD CONSTRAINT fk_dimension_types_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE prompt_template ADD CONSTRAINT fk_prompt_template_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE email_server ADD CONSTRAINT fk_email_server_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE workflow ADD CONSTRAINT fk_workflow_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE action_flows ADD CONSTRAINT fk_action_flows_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE chat_configuration ADD CONSTRAINT fk_chat_configuration_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE llm_configuration ADD CONSTRAINT fk_llm_configuration_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE customer_clients ADD CONSTRAINT fk_customer_clients_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE emails ADD CONSTRAINT fk_emails_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE dimensions ADD CONSTRAINT fk_dimensions_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE prompt ADD CONSTRAINT fk_prompt_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE user_email_settings ADD CONSTRAINT fk_user_email_settings_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE tools ADD CONSTRAINT fk_tools_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE agent ADD CONSTRAINT fk_agent_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE conversations ADD CONSTRAINT fk_conversations_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE entities ADD CONSTRAINT fk_entities_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE files ADD CONSTRAINT fk_files_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE answers ADD CONSTRAINT fk_answers_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE questions ADD CONSTRAINT fk_questions_customer_uuid FOREIGN KEY (customer_uuid)
REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE;

ALTER TABLE customer_client_tier_application_mapping
DROP CONSTRAINT customer_client_tier_application_mapp_customer_client_uuid_fkey;

ALTER TABLE customer_client_tier_application_mapping
ADD CONSTRAINT customer_client_tier_application_mapping_customer_client_uuid_f
FOREIGN KEY (customer_client_uuid) REFERENCES customer_clients(customer_client_uuid) ON DELETE CASCADE;

