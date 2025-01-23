-- Configuration specific tables

-- This table is used to store different dimension types configured through the platform
-- Example values - Intent, Sentiment, Geography_Country, Geography_State, Customer_Tier
CREATE TABLE IF NOT EXISTS dimension_type (
    dimension_type_uuid VARCHAR(45) PRIMARY KEY,
    dimension_type_name VARCHAR(255) NOT NULL, -- Geography, Intent, Sentiment, Customer Tier
    is_deleted BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(dimension_type_name)
);


CREATE TABLE IF NOT EXISTS dimension_type_customer_application_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    dimension_type_uuid VARCHAR(45) NOT NULL,
    description TEXT,
    dimension_type_details_json JSONB,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(dimension_type_uuid, application_uuid, customer_uuid),
    FOREIGN KEY (dimension_type_uuid) REFERENCES dimension_type(dimension_type_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store different dimension under specific dimension types configured through the platform
-- Example - Inside Geography dimension type - USA can be one of the dimension
-- For Intent dimension type - PURCHASE_ORDER_STATUS can be one of the dimension
CREATE TABLE IF NOT EXISTS dimension (
    dimension_uuid VARCHAR(45) PRIMARY KEY,
    dimension_name VARCHAR(255) NOT NULL,
    dimension_type_uuid VARCHAR(45) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(dimension_name),
    FOREIGN KEY (dimension_type_uuid) REFERENCES dimension_type(dimension_type_uuid) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS dimension_customer_application_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    dimension_uuid VARCHAR(45) NOT NULL,
    description TEXT,
    dimension_details_json JSONB,
    parent_dimension_uuid VARCHAR(45), -- Parent dimension UUID, For a customer application mapping the parent dimension can differ
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,  -- If there is a functionality to enable or disable that dimension for a particular customer and application mapping
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(dimension_uuid, application_uuid, customer_uuid),
    FOREIGN KEY (dimension_uuid) REFERENCES dimension(dimension_uuid) ON DELETE CASCADE,
    FOREIGN KEY (parent_dimension_uuid) REFERENCES dimension(dimension_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store prompt categories - metadata table -- INTENT_AND_SENTIMENT_CLASSIFICATION, CUSTOMER_AND_GEOGRAPHY_IDENTIFICATION,
-- DETAILS_EXTRACTION, SUMMARY_AND_RESPONSE_GENERATION
CREATE TABLE IF NOT EXISTS prompt_category (
    prompt_category_uuid VARCHAR(45) PRIMARY KEY,
    prompt_category_name VARCHAR(255) NOT NULL,
    description TEXT,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(prompt_category_name)
);


-- This table is used to store different prompt templates configured through the platform
-- Prompt template is a format which can be used to generate prompts
CREATE TABLE IF NOT EXISTS prompt_template (
    prompt_template_uuid VARCHAR(45) PRIMARY KEY,
    prompt_template_name VARCHAR(255) NOT NULL,
    prompt_category_uuid VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(prompt_template_name),
    FOREIGN KEY (prompt_category_uuid) REFERENCES prompt_category(prompt_category_uuid) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS prompt_template_customer_application_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    prompt_template_uuid VARCHAR(45) NOT NULL,
    description TEXT,
    prompt_template_details_json JSONB,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(prompt_template_uuid, application_uuid, customer_uuid),
    FOREIGN KEY (prompt_template_uuid) REFERENCES prompt_template(prompt_template_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store prompts configured through the platform
-- A prompt is a natural language text that requests the generative AI to perform a specific task.
-- write dimension values enumeration to the prompt ...
CREATE TABLE IF NOT EXISTS prompt (
    prompt_uuid VARCHAR(45) PRIMARY KEY,
    prompt_name VARCHAR(255) NOT NULL,
    prompt_category_uuid VARCHAR(255) NOT NULL,
    prompt_details_json JSONB,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(prompt_name, application_uuid, customer_uuid),
    FOREIGN KEY (prompt_category_uuid) REFERENCES prompt_category(prompt_category_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store metadata for each llm_provider
CREATE TABLE IF NOT EXISTS llm_provider_meta_data (
    llm_provider_uuid VARCHAR(45) PRIMARY KEY,
    llm_provider_name VARCHAR(255) NOT NULL,
    llm_provider_details_json JSONB, -- storing provider related meta data (model , api_type)
    llm_column_details JSONB, -- [{key: 'model', 'type':'dropdown'},{'key':'deployment_name','type':'input'}]
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(llm_provider_name)
);


-- This table is used to store the llm configuration for an organization and application combination
CREATE TABLE IF NOT EXISTS llm_configuration (
    llm_configuration_uuid VARCHAR(45) PRIMARY KEY,
    llm_configuration_name VARCHAR(255) NOT NULL,
    llm_provider_uuid VARCHAR(45),
    llm_configuration_details_json JSONB, -- (API key should be stored in azure key vault, its url is stored here),
                                          -- Deployment_Name, API_Base, Model_Name, API_Type, API_Version
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(llm_configuration_name, customer_uuid),
    FOREIGN KEY (llm_provider_uuid) REFERENCES llm_provider_meta_data(llm_provider_uuid) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store tools(custom or builtin) added through the platform
-- Tools can be just about anything — APIs, functions, databases, etc.
CREATE TABLE IF NOT EXISTS tool(
    tool_uuid VARCHAR(45) PRIMARY KEY,
    tool_name VARCHAR(255) NOT NULL,
    tool_details_json JSONB,
    is_built_in BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(tool_name)
);


CREATE TABLE IF NOT EXISTS tool_customer_application_mapping(
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    tool_uuid VARCHAR(45) NOT NULL,
    description TEXT,
    tool_details_json JSONB, -- parameters ,methods,parameters type,response type, any code
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(tool_uuid, application_uuid, customer_uuid),
    FOREIGN KEY (tool_uuid) REFERENCES tool(tool_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store agents and the respective tool and prompt details which the agent uses.
CREATE TABLE IF NOT EXISTS agent(
    agent_uuid VARCHAR(45) PRIMARY KEY,
    agent_name VARCHAR(255) NOT NULL,
    dimension_details_json JSONB,
    agent_details_json JSONB, -- prompt,tools list and any extra information
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(agent_name)
);


-- agent tool prompt mapping table ? required or not
CREATE TABLE IF NOT EXISTS agent_customer_application_mapping(
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    agent_uuid VARCHAR(45) NOT NULL,
    description TEXT,
    agent_details_json JSONB, -- prompt,tools list and any extra information
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(agent_uuid, application_uuid, customer_uuid),
    FOREIGN KEY (agent_uuid) REFERENCES agent(agent_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store the customers for an organization and its respective details
CREATE TABLE IF NOT EXISTS customer_client (
    customer_client_uuid VARCHAR(45) PRIMARY KEY,
    customer_client_geography_uuid VARCHAR(45), -- Geography UUID
    customer_client_domain_name VARCHAR(255),
    customer_client_name VARCHAR(255) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    customer_client_address TEXT,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(customer_client_name,customer_uuid),
    FOREIGN KEY (customer_client_geography_uuid) REFERENCES dimension(dimension_uuid) ON DELETE SET NULL,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store the mapping customers for an organization and its respective tier under an application
CREATE TABLE IF NOT EXISTS customer_client_tier_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    customer_client_uuid VARCHAR(45) NOT NULL,
    tier_mapping_uuid VARCHAR(45) NOT NULL,
    extractor_template_details_json JSONB,
    insert_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(customer_client_uuid,tier_mapping_uuid),
    FOREIGN KEY (tier_mapping_uuid) REFERENCES dimension_customer_application_mapping(mapping_uuid) ON DELETE CASCADE,
    FOREIGN KEY (customer_client_uuid) REFERENCES customer_client(customer_client_uuid) ON DELETE CASCADE  -- A customer client will always be in only one tier inside an application
);


-- This table is used to store the users information of customer users, of an organization
CREATE TABLE IF NOT EXISTS client_user (
    client_user_uuid VARCHAR(45) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email_id VARCHAR(255) NOT NULL,
    geography_uuid VARCHAR(45),  -- Geography of the user
    customer_client_uuid VARCHAR(45) NOT NULL,
    user_info_json JSONB, -- add required information
    status BOOLEAN DEFAULT TRUE, -- TRUE means user active. False - Inactive/Disabled
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(email_id),
    FOREIGN KEY (customer_client_uuid) REFERENCES customer_client(customer_client_uuid) ON DELETE CASCADE,
    FOREIGN KEY (geography_uuid) REFERENCES dimension(dimension_uuid) ON DELETE SET NULL
);


-- This table is used to store the email_server configured for an organization under an application
CREATE TABLE IF NOT EXISTS email_server (
    email_server_uuid VARCHAR(45) PRIMARY KEY,
    server_type VARCHAR(255) NOT NULL,
    server_url VARCHAR(255) NOT NULL,
    email_provider_name VARCHAR(255) NOT NULL,
    port VARCHAR(45) NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS email_server_customer_application_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    email_server_uuid VARCHAR(45) NOT NULL,
    is_ssl_enabled BOOLEAN DEFAULT TRUE,
    sync_time_interval BIGINT DEFAULT 5,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(email_server_uuid, application_uuid, customer_uuid),
    FOREIGN KEY (email_server_uuid) REFERENCES email_server(email_server_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store the email ids(group/individual) configured for an organization under an application
CREATE TABLE IF NOT EXISTS user_email_setting (
    user_email_uuid  VARCHAR(45) PRIMARY KEY,
    email_id VARCHAR(255) NOT NULL UNIQUE, -- email
    encrypted_password VARCHAR(255) NOT NULL,
    email_type VARCHAR(255) NOT NULL,
    email_details_json JSONB,
    is_primary_sender_address BOOLEAN DEFAULT FALSE,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    last_read_ts TIMESTAMP,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(email_id, application_uuid, customer_uuid),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store chat configuration information
-- the icons, avatar information and embed code
CREATE TABLE IF NOT EXISTS chat_configuration (
    chat_configuration_uuid VARCHAR(45) PRIMARY KEY,
    chat_configuration_name VARCHAR(255) NOT NULL,
    chat_configuration_type VARCHAR(255) NOT NULL,  -- (landing/intent page)
    chat_configuration_provider VARCHAR(255) NOT NULL, -- chat_provider details - whatsapp , web
    chat_details_json JSONB, --CSS template Details & details Json
    code TEXT,
    status BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS chat_configuration_customer_application_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    chat_configuration_uuid VARCHAR(45),
    description TEXT,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(chat_configuration_uuid, application_uuid, customer_uuid),
    FOREIGN KEY (chat_configuration_uuid) REFERENCES chat_configuration(chat_configuration_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- Can we move these tables to NOSQL databases
-- This table is used to store an email_conversation object.
CREATE TABLE IF NOT EXISTS email_conversation (
    email_conversation_uuid VARCHAR(45) PRIMARY KEY,
    customer_client_uuid VARCHAR(45),
    email_conversation_flow_status VARCHAR(255),  -- Need assistance, etc
    email_activity JSONB, -- activity log (timelines and summary) -- who sent or received email information in timeline
    dimension_uuid VARCHAR(45),  -- Intent uuid
    application_uuid VARCHAR(45) NOT NULL, -- application_uuid where the email address was added to which the email was received
    customer_uuid VARCHAR(45) NOT NULL,
    assigned_to VARCHAR(45),  -- Foreign key referencing users table (user_id)
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (customer_client_uuid) REFERENCES customer_client(customer_client_uuid) ON DELETE SET NULL,
    FOREIGN KEY (dimension_uuid) REFERENCES dimension(dimension_uuid) ON DELETE SET NULL,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES usermgmt.users(user_id) ON DELETE SET DEFAULT  --foreign key constraint for assigned_to
);


-- This table is used to store each email data with unique email_uuid(gmail message id).
-- If an email has multiple emails,to identify all the emails belong to the same email_conversation
CREATE TABLE IF NOT EXISTS email (
    email_uuid VARCHAR(100) PRIMARY KEY,  -- gmail message id
    email_conversation_uuid VARCHAR(45) NOT NULL,
    email_subject VARCHAR(255),
    email_status VARCHAR(255) NOT NULL,  -- Sent/Received/Draft
    dimension_action_json JSONB, -- Geography,Intent,Sentiment,customer Tier details information, and Action flow details
    role_uuid VARCHAR(45), -- OverAllCSRManager/CSR Manager/CSR
    parent_uuid VARCHAR(100),
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (email_conversation_uuid) REFERENCES email_conversation(email_conversation_uuid) ON DELETE CASCADE,
    FOREIGN KEY (parent_uuid) REFERENCES email(email_uuid) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES usermgmt.users(user_id),
    FOREIGN KEY (role_uuid) REFERENCES usermgmt.roles(role_id)
);


CREATE TABLE IF NOT EXISTS email_info_detail (
    email_info_uuid VARCHAR(45) PRIMARY KEY,
    email_uuid VARCHAR(100) NOT NULL,
    email_body_url TEXT,
    attachments JSONB,
    sender TEXT,
    sender_name TEXT,
    email_type VARCHAR(255),
    recipient_name TEXT,
    recipient TEXT,
    recipients JSONB,
    cc_recipients JSONB,
    bcc_recipients JSONB,
    email_body_summary TEXT,
    email_meta_body TEXT, -- first 200 chars of email_body
    html_body TEXT,
    extracted_order_details TEXT,
    validated_details TEXT,
    verified BOOLEAN DEFAULT NULL,
    FOREIGN KEY (email_uuid) REFERENCES email(email_uuid) ON DELETE CASCADE
);


-- This table is used to store all the details related to the chat conversations
-- Queries --
-- list of csr uuids and not the meta_info required (csr_info_json)
-- authenticated and non-authenticated - how a user is defined as such? (user_details_json)
-- how to handle client users for email and chat mode of communication - authentication
-- skill mapping -- to know which user a conversation can be assigned
CREATE TABLE chat_conversation (
    chat_conversation_uuid VARCHAR(45) PRIMARY KEY,
    user_details_json JSONB,   -- {uid: number,name: Name,userType: {AUTHENTICATED,NON_AUTHENTICATED},profilePicture: azure storage},
    conversation_status VARCHAR(100) NOT NULL, -- AI_ONGOING,UNASSIGNED,ONGOING_AGENT,RESOLVED
    csr_info_json JSONB, -- { // array because a chat could be escalated between multiple agents, in case the bot completely handles a chat and never triggers a human handoff this array would be empty
                          -- csr uuid: number,
                          -- name: Name,
                          -- profilePicture: azure storage
                         -- }
    csr_hand_off BOOLEAN DEFAULT false, -- it is essentially to capture if a humanHandoff was triggered by the bot or not
    conversation_stats_json JSONB, -- eventTiming: EventTiming {conversationStartTime: TIMESTAMP, humanHandoffTime: TIMESTAMP, firstAgentAssignmentTime: TIMESTAMP,firstAgentMessageTime: TIMESTAMP,lastUserMessageTime: TIMESTAMP,lastAgentMessageTime: TIMESTAMP,conversationResolutionTime: TIMESTAMP}
    conversation_feedback_transaction_json JSONB, -- after the conversation is resolved, user app will request the user to submit the
                                                  -- feedback for this particular conversation  {satisfactionScoreOnTen: number,additionalComments: string},
    summary TEXT NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    message_details_json JSONB,--id VARCHAR(45),user_id VARCHAR(45),--User id & CSR ID,csr_id VARCHAR(45),source  VARCHAR(45),-- bot,csr,user ,message_marker VARCHAR(255), --LOGGED,DELIVERED, READ,    dimension_action_json JSONB,-- dimension & Action will store here,message_text TEXT NOT NULL,media_url VARCHAR(255),parent_message_uuid VARCHAR(45),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store workflow configured for a organization for a use case(application)
CREATE TABLE IF NOT EXISTS wiseflow (
    wiseflow_uuid VARCHAR(45) PRIMARY KEY,
    wiseflow_name VARCHAR(255) NOT NULL,
    description TEXT,
    wiseflow_details_json JSONB,
    customer_uuid VARCHAR(45) NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    channel_uuid VARCHAR(45),
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(customer_uuid, application_uuid, channel_uuid),
    FOREIGN KEY (channel_uuid) REFERENCES usermgmt.customer_resource_action_mapping(customer_resource_action_id) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table is used to store individual steps in a workflow.
CREATE TABLE IF NOT EXISTS step (
    step_uuid VARCHAR(45) PRIMARY KEY,
    wiseflow_uuid VARCHAR(45) NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    description TEXT,
    step_details_json JSONB,
    step_type VARCHAR(255),
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (wiseflow_uuid) REFERENCES wiseflow(wiseflow_uuid) ON DELETE CASCADE
);


-- This table will store info related to wiseflow, entity(email or chat), entity_type, and step details, extra information if required - wiseflow_execution_info
CREATE TABLE IF NOT EXISTS wiseflow_execution_details (
    execution_details_uuid VARCHAR(45) PRIMARY KEY,
    entity_uuid VARCHAR(45) NOT NULL,  -- email_conversation_uuid chat_conversation_uuid
    entity_type VARCHAR(255) NOT NULL,  -- email/chat/etc
    step_uuid VARCHAR(45) NOT NULL,
    wiseflow_uuid VARCHAR(45) NOT NULL,
    wiseflow_execution_info JSONB,
    FOREIGN KEY (wiseflow_uuid) REFERENCES wiseflow(wiseflow_uuid) ON DELETE CASCADE,
    FOREIGN KEY (step_uuid) REFERENCES step(step_uuid) ON DELETE CASCADE
);


CREATE TABLE api_configuration (
    api_configuration_uuid VARCHAR(45) PRIMARY KEY,
    api_name VARCHAR(255) NOT NULL,  -- API name or identifier
    endpoint VARCHAR(255) NOT NULL,  -- API endpoint
    method VARCHAR(10) NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),  -- HTTP method
    description TEXT,
    params_details_json JSONB, -- json of param keys and values
    is_deleted BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT TRUE, --To differentiate apis which are exposed by Vassar Team and respective customer
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);


-- If an api has 10 headers, here 10 records will be created, is it a good approach.
CREATE TABLE api_header (
    api_header_uuid VARCHAR(45) PRIMARY KEY,
    api_configuration_uuid VARCHAR(45) NOT NULL,  -- Link to the API configuration
    header_type VARCHAR(45) NOT NULL CHECK (header_type IN ('Response headers', 'Request headers')),
    header_key VARCHAR(255) NOT NULL,  -- Header key (e.g., Authorization, Content-Type)
    header_value VARCHAR(255),  -- Default header value (optional, can be left null for dynamic values like api_key)
    is_required BOOLEAN NOT NULL DEFAULT TRUE,  -- Whether the header is mandatory
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (api_configuration_uuid) REFERENCES api_configuration(api_configuration_uuid) ON DELETE CASCADE
);


CREATE TABLE api_body_template (
    api_body_template_uuid VARCHAR(45) PRIMARY KEY,
    api_configuration_uuid VARCHAR(45) NOT NULL,   -- Link to the API configuration
    api_payload TEXT,  -- payload
    is_deleted BOOLEAN DEFAULT FALSE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (api_configuration_uuid) REFERENCES api_configuration(api_configuration_uuid) ON DELETE CASCADE
);


--For Each customer we have different api_keys ,for that we placed auth_value inside this mapping table
CREATE TABLE api_configuration_customer_application_mapping (
    mapping_uuid VARCHAR(45) PRIMARY KEY,
    customer_uuid VARCHAR(45) NOT NULL,  -- Unique identifier for the customer
    application_uuid VARCHAR(45) NOT NULL,  -- Unique identifier for the application
    api_configuration_uuid VARCHAR(45),  -- Link to the API configuration
    auth_value JSONB,  -- Authorization value (e.g., token, API key)auth_key and auth_value  -----azure key store reference will be added here
    status BOOLEAN DEFAULT TRUE,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (api_configuration_uuid) REFERENCES api_configuration(api_configuration_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- This table stores the metadata for all the states in a country, shown in the states dropdown in application
CREATE TABLE IF NOT EXISTS countries (
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
    emojiU character varying(191),
    created_at timestamp without time zone,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    flag smallint DEFAULT 1 NOT NULL,
    wikiDataId character varying(255)
);


-- This table stores the metadata for all the states in a country, shown in the states dropdown in application
CREATE TABLE IF NOT EXISTS states (
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
    wikiDataId character varying(255),
    FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE
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

-- every application has few entities which are like categories among which files can be segregated
-- every entity can have multiple attributes and each attribute can have multiple values
CREATE TABLE entities (
    entity_uuid VARCHAR(45) PRIMARY KEY,
    entity_name VARCHAR(30) NOT NULL,
    entity_description TEXT,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    attribute_details_json JSONB,    -- all the attributes and attribute values of that entity
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- table to store the data sources added to an application
-- knowledge from these sources will be extracted and used to answer questions in that application
CREATE TABLE knowledge_sources(
    knowledge_source_uuid VARCHAR(45) PRIMARY KEY,
    knowledge_source_name VARCHAR(254) NOT NULL,
    knowledge_source_path TEXT NOT NULL,    -- azure storage blob url
    knowledge_source_type VARCHAR(30) NOT NULL,    -- pdf, word, web etc.
    knowledge_source_status VARCHAR(30) NOT NULL,    -- under review, reviewed etc.
    knowledge_source_metadata JSONB,    -- no.of pages, language, no.of web pages scraped, video length
    parent_knowledge_source_uuid VARCHAR(45),    -- reference to original knowledge source in case of a reupload
    is_deleted BOOLEAN DEFAULT FALSE,    -- in case a deleted knowledge source needs restoration
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    entity_uuid VARCHAR(45) NOT NULL,
    attribute_details_json JSONB,    -- attributes and attribute values mapped to the knowledge source
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (entity_uuid) REFERENCES entities(entity_uuid) ON DELETE SET NULL,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- media table to store the media such as images that have been extracted from knowledge sources
-- every media will be mapped to a knowledge source and will be used in answers given to queries
CREATE TABLE media(
    media_uuid VARCHAR(45) PRIMARY KEY,
    media_name VARCHAR(254) NOT NULL,   -- name of the extracted image Figure 10, Table 18 etc.
    media_path TEXT NOT NULL,     -- azure storage blob url
    media_details_json JSONB,   -- for saving page no., description etc. will no be queried
    knowledge_source_uuid VARCHAR(45),
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- errors that were found during the knowledge source parsing will be saved in errors table
-- the errors of a knowledge source can be corrected
CREATE TABLE errors(
    error_uuid VARCHAR(45) PRIMARY KEY,
    error_type VARCHAR(30) NOT NULL,    -- page error, table error etc.
    error_status VARCHAR(30) NOT NULL,    -- resolved, unresolved etc.
    knowledge_source_uuid VARCHAR(45) NOT NULL,
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (knowledge_source_uuid) REFERENCES knowledge_sources(knowledge_source_uuid) ON DELETE CASCADE,
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- the drafts table saves the answers that are partially modified and saved for later modifications
-- drafts when updated will become answers
create TABLE drafts(
    draft_uuid VARCHAR(45) PRIMARY KEY,
    draft TEXT,
    attachment_details_json JSONB,    -- media uuids for images, knowledge_source uuids for videos
    author_user_uuid VARCHAR(45),
    author_role_uuid VARCHAR(45),
    answer_uuid VARCHAR(45),
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- answers table contains the answers along with media to questions asked in an application
-- multiple questions can have same answer, answers can also be edited, verified
CREATE TABLE answers(
    answer_uuid VARCHAR(45) PRIMARY KEY,
    answer TEXT,
    attachment_details_json JSONB,    -- media uuids for images, knowledge_source uuids for videos
    draft_uuid VARCHAR(45),    -- uuid of the draft id saved, can be NULL
    file_details_json JSONB,    -- store the knowledge_source uuids of answer sources
    entity_details_json JSONB,    -- the entity uuids of corresponding knowledge_source uuids
    feedback TEXT,
    is_verified BOOLEAN,
    verifier_user_uuid VARCHAR(45),
    verifier_role_uuid VARCHAR(45),
    is_system_generated BOOLEAN,
    author_user_uuid VARCHAR(45),
    author_role_uuid VARCHAR(45),
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);


-- the questions that have been asked or generated from the knowledge sources in an application
-- question uuids will be saved as metadata in chroma cache
CREATE TABLE questions (
    question_uuid VARCHAR(45) PRIMARY KEY,
    question TEXT,
    answer_uuid VARCHAR(45) NOT NULL,
    in_cache BOOLEAN DEFAULT TRUE,    -- if true similarity search will be performed in chroma
    is_system_generated BOOLEAN,
    author_user_uuid VARCHAR(45),
    author_role_uuid VARCHAR(45),
    application_uuid VARCHAR(45) NOT NULL,
    customer_uuid VARCHAR(45) NOT NULL,
    inserted_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY(answer_uuid) REFERENCES answers(answer_uuid),
    FOREIGN KEY (application_uuid) REFERENCES usermgmt.applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_uuid) REFERENCES usermgmt.customers(customer_id) ON DELETE CASCADE
);

