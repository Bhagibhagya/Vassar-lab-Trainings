DOCUMENT_NAME = "DOE O 226.1B" # All documents:: "DOE O 226.1B","DOE O 414.1D","10 CFR Part 830 Subpart A."
GUIDELINES_COLLECTION_NAME = "doe_guidelines"
CUSTOMER_ID_UCOR = "8d59b20a-3a56-4579-8821-9f2d4915ed20"

TEST_CLAUSES_ONLY_TWO = [
    {
      "clause": "The contractor must establish and implement processes to detect and prevent quality problems.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "2",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "The contractor must identify, control, and correct items, services, and processes that do not meet established requirements.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "2",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    }
]


TEST_CLAUSES = [
    {
      "clause": "The contractor must train and qualify personnel to be capable of performing their assigned work.",
      "type_of_clause": "QAP",
      "independent": "true",
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "2",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "The contractor must provide continuing training to personnel to maintain their job proficiency.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "2",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "The contractor must establish and implement processes to detect and prevent quality problems.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "2",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "The contractor must identify, control, and correct items, services, and processes that do not meet established requirements.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "2",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "The contractor must perform work consistent with technical standards, administrative controls, and other hazard controls adopted to meet regulatory or contract requirements.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "2",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "Contractor must ensure persons who perform independent assessments are technically qualified and knowledgeable in the areas to be assessed.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "3",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "Contractor must verify or validate work before approval and implementation of the design.",
      "type_of_clause": "QAC",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "3",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "Contractor must establish and implement processes to ensure that approved suppliers continue to provide acceptable items and services.",
      "type_of_clause": "QAP",
      "independent": 'true',
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "3",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    },
    {
      "clause": "The contractor must annually submit any changes to the DOE-approved QAP to DOE for approval.",
      "type_of_clause": "QAP",
      "independent": "true",
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "1",
        "File Name": "10 CFR Part 830 Subpart A."
        }
    },
    {
      "clause": "The contractor responsible for a DOE nuclear facility must submit a QAP to DOE for approval.",
      "type_of_clause": "QAP",
      "independent": "true",
      "reason": "The clause does not reference any external material.",
      "reference": {
        "Page No": "1",
        "File Name": "10 CFR Part 830 Subpart A."
      }
    }
]



TEST_CLAUSES_V2 = [
        {
            "id": "e097a540-333b-4a3b-82d4-826dc3f0db27",
            "document": "# Implementation of Department of Energy Oversight Policy\n\n## 4. Requirements\n\n### c. Performance Expectations\n- DOE line management must:\n  - Establish and communicate performance expectations to contractors through formal contract mechanisms.\n  - Set expectations such as:\n    - Safety performance measures\n    - Commitments\n  - Establish these expectations on an annual basis, or as otherwise required or determined appropriate by the Field Element.\n\n### d. Communication of Oversight Results\n- DOE line management must have:\n  - Effective processes for communicating oversight results and other issues in a timely manner.\n  - Communication should occur:\n    - Up the line management chain\n    - To the contractor as appropriate\n  - This communication must be sufficient to allow senior managers to make informed decisions.\n\n### e. Oversight Processes for Government-Owned and Government-Operated Facilities\n- For activities and programs at Government-owned and Government-operated facilities and sites that are not under the cognizance of a DOE Field Element:\n  - DOE Headquarters program offices must:\n    - Establish and implement comparably effective oversight processes.\n    - Ensure these processes are consistent with:\n      - Requirements for the contractor assurance system (see attachment 1)\n      - DOE line management oversight processes.",
            "type_of_clause": "Consultant_Clause",
            "reason_for_clause": "This clause specifies the actions that DOE line management must take regarding performance expectations for contractors.",
            "independent": "true",
            "reason": "This clause is a direct requirement for the actions of DOE line management towards contractors.",
            "references": [
                "DOE_O_226_1B.pdf",
                "4"
            ]
        },
        {
            "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
            "document": "# Contractor Assurance System \n\n## 1. Responsibilities\n- The contractor is responsible for complying with the requirements of this Contractor Requirements Document (CRD), regardless of who performs the work.\n- The contractor must flow down the requirements of this CRD to subcontractors at any tier as necessary to ensure compliance.\n- Contractors are required to:\n  - Monitor and evaluate all work performed under their contracts.\n  - Ensure that the work of subcontractors meets applicable requirements for:\n    - Environment\n    - Safety and health\n    - Quality assurance\n    - Integrated safety management\n    - Safeguards and security\n    - Cyber security\n    - Business and financial systems\n    - Emergency management\n\n## 2. Requirements\n- The contractor must establish an assurance system that includes:\n  - Assignment of management responsibilities and accountabilities.\n  - Evidence to assure both the Department of Energy (DOE) and the contractor’s management that:\n    - Work is being performed safely and securely.\n    - Compliance with all requirements is maintained.\n    - Risks are being identified and managed.\n    - Systems of control are effective and efficient.",
            "type_of_clause": "Consultant_Clause",
            "reason_for_clause": "This clause directly imposes a requirement on the contractor to comply with the CRD.",
            "independent": "true",
            "reason": "This clause stands alone as a clear directive to the contractor.",
            "references": [
                "DOE_O_226_1B.pdf",
                "9"
            ]
        },
        {
            "id": "642add36-581c-4125-80cb-339dd0102c3d",
            "document": "# Contractor Assurance System \n\nThe Contractor Assurance System must include the following key components:\n\n## 1. Validation of Assurance System Processes\n- A method for validating the effectiveness of assurance system processes is essential.\n- Possible methods include:\n  - Third-party audits\n  - Peer reviews\n  - Independent assessments\n  - External certification\n- These methods should complement, but not replace, internal assurance systems.\n\n## 2. Self-Assessment and Improvement Activities\n- The system must incorporate rigorous, risk-informed, and credible self-assessment and feedback mechanisms.\n- Assessment programs should be:\n  - Risk-informed\n  - Formally described and documented\n  - Appropriately cover potentially high-consequence activities\n\n## 3. Structured Issues Management System\n- A structured issues management system must be:\n  - Formally described and documented\n  - Capable of capturing program and performance deficiencies (both individually and collectively)\n  - Designed to provide timely reporting and compensatory corrective actions when necessary\n\n### Key Features of the Issues Management System:\n- **Categorization of Findings**: \n  - The system must categorize the significance of findings based on risk, priority, and other appropriate factors.\n  - This enables contractor management to evaluate and correct problems in a timely manner.\n\n- **Higher Significance Findings**: \n  - For issues categorized as higher significance findings, contractor management must ensure the following activities are completed and documented:\n    - [Further details on activities to be completed and documented would be included here.]\n\nThis structured approach ensures that the contractor assurance system is effective, responsive, and capable of continuous improvement.",
            "type_of_clause": "Consultant_Clause",
            "reason_for_clause": "This clause specifies a minimum requirement for the contractor's assurance system.",
            "independent": "true",
            "reason": "This clause is a standalone requirement for the contractor's assurance system.",
            "references": [
                "DOE_O_226_1B.pdf",
                "10, 9"
            ]
        },
        {
            "id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809",
            "document": "# Contractor Assurance System \n\n## Key Components\n\n1. **Timely Communication**\n   - Ensure appropriate communication with the Contracting Officer.\n   - Provide electronic access to assurance-related information.\n\n2. **Continuous Feedback and Improvement**\n   - Implement worker feedback mechanisms, such as:\n     - Employee concerns programs\n     - Telephone hotlines\n     - Employee suggestions forms\n     - Labor organization input\n   - Focus on improvements in:\n     - Work planning\n     - Hazard identification activities\n     - Lessons learned programs\n\n3. **Metrics and Targets**\n   - Establish metrics and targets to assess performance effectiveness.\n   - Benchmark key functional areas against:\n     - Other DOE contractors\n     - Industry standards\n     - Research institutions\n\n## Submission Requirements\n\n- The contractor must submit an initial description of the contractor assurance system to the Contracting Officer for DOE review and approval. This description must include:\n  - Clear definitions of processes\n  - Key activities\n  - Accountabilities\n\n- If necessary, an implementation plan should be submitted that:\n  - Considers and mitigates risks\n  - Encompasses all facilities, systems, and organizational elements\n\n## Notification of Changes\n\n- Once the description is approved, the contractor must provide timely notification to the Contracting Officer regarding any significant changes to the assurance system **prior** to implementing those changes.",
            "type_of_clause": "Consultant_Clause",
            "reason_for_clause": "This clause requires the contractor to submit a specific document for review and approval.",
            "independent": "true",
            "reason": "This clause is a clear directive that stands alone.",
            "references": [
                "DOE_O_226_1B.pdf",
                "10, 11"
            ]
        },
        {
            "id": "ee02e075-3ff2-4e5a-a7a3-ac6c009a9e48",
            "document": "# Contractor Assurance System \n\n## Overview\nThe Contractor Assurance System is designed to ensure appropriate oversight of contractor activities. It emphasizes the importance of documentation and data availability for effective monitoring and evaluation.\n\n## Key Requirements\n\n- **Documentation and Availability**\n  - Contractor assurance system data must be:\n    - Documented\n    - Readily available to the Department of Energy (DOE)\n\n- **Analysis and Reporting**\n  - Results of assurance processes must be:\n    - Analyzed\n    - Compiled\n    - Reported to the DOE as requested by the Contracting Officer\n\n## Purpose of Reporting\nThe reporting of assurance process results serves several purposes, including:\n- Supporting contractor evaluations\n- Assisting in the review and approval of corrective action plans\n\nBy adhering to these requirements, the Contractor Assurance System aims to maintain high standards of oversight and accountability in contractor operations.",
            "type_of_clause": "Consultant_Clause",
            "reason_for_clause": "This clause requires the contractor to analyze and report assurance process results.",
            "independent": "true",
            "reason": "This clause is a clear directive that stands alone.",
            "references": [
                "DOE_O_226_1B.pdf",
                "11"
            ]
        }
  ]


FINAL_CLAUSES_414 = [
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must include the work of subcontractors in their monitoring and evaluation.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for environment.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for safety.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for health.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for quality assurance.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for integrated safety management.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for safeguards and security.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for cyber security.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for business and financial systems.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "Contractor must ensure work performance meets the applicable requirements for emergency management.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "The contractor must establish an assurance system that includes assignment of management responsibilities and accountabilities.",
        "type_of_clause": "Consultant_Clause",
        "reference": [
            "DOE_O_226_1B",
            "9"
        ]
    },

]


DEMO_RESPONSE = {
  "message": "Documents are Validated",
  "results": [
    {
      "Project ID": "PROC-PQ-1610",
      "total_clauses": [
        {
          "clause": "The contractor must establish and implement processes to detect and prevent quality problems.",
          "compliance_status": "Fully Meeting",
          "chunk_ids": [
            {
              "chunk_id": "3ca89186-53aa-4f62-a583-be5c6584da3f",
              "chunk_content": "o establish and implement processes to detect and prevent quality problems. o identify, control, and correct items, services, and processes that do not meet established requirements. o identify the causes of problems and work to prevent recurrence as part of correcting a problem. o review item characteristics, process implementation, and other quality related information to identify items, services, and process needing improvement.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "9",
              "reasoning": "This chunk explicitly states the requirement to establish and implement processes to detect and prevent quality problems, which directly aligns with the clause."
            },
            {
              "chunk_id": "f34febb8-dc3b-4e8c-98b1-e4ffac1e33d1",
              "chunk_content": "This procedure establishes the United Cleanup Oak Ridge LLC (UCOR) process for the identification, evaluation, reporting, and tracking of noncompliances with the U.S. Department of Energy (DOE) nuclear and criticality safety requirements enforceable under the Price-Anderson Amendments Act (PAAA) and its implementing regulations, Worker Safety and Health (WSH) requirements enforceable under 10 Code of Federal Regulations (CFR) 851, and Classified Information Security (CIS) requirements enforceable under 10 CFR 824.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "3",
              "reasoning": "This chunk describes the processes established for identifying and tracking noncompliances, which is a critical aspect of detecting quality problems."
            },
            {
              "chunk_id": "6fd77c4f-354d-49d2-8b19-bd96dadd0b07",
              "chunk_content": "PURPOSE This procedure establishes the United Cleanup Oak Ridge LLC (UCOR) process for the identification, evaluation, reporting, and tracking of noncompliances with the U.S. Department of Energy (DOE) nuclear and criticality safety requirements enforceable under the Price-Anderson Amendments Act (PAAA) and its implementing regulations, Worker Safety and Health (WSH) requirements enforceable under 10 Code of Federal Regulations (CFR) 851, and Classified Information Security (CIS) requirements enforceable under 10 CFR 824.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "3",
              "reasoning": "This chunk reiterates the establishment of processes for identifying and addressing noncompliances, which is essential for preventing quality issues."
            },
            {
              "chunk_id": "2022991b-a421-4761-9828-c1247690191b",
              "chunk_content": "Screen the following sources, as a minimum: • Occurrence Reports (ORPS) • Management Assessments • Radiological Incident Report Forms • Conditions Adverse to Quality • Nonconformance Reports (NCRs) • Anomalous Condition Reports • Internal safety and health findings reported to Issues Management • External Assessments, Audits, and Investigations",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "3",
              "reasoning": "This chunk outlines the sources to be screened for quality issues, indicating a proactive approach to detecting potential problems."
            },
            {
              "chunk_id": "587bf66f-d61a-4469-a0bb-b3ace029f782",
              "chunk_content": "This table outlines the roles and responsibilities for handling various compliance and enforcement matters within a nuclear safety organization. The document details procedures for managing Employee Concerns, PAAA enforcement, and security-related issues through the Corrective Action Management System (CAMS).",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "4",
              "reasoning": "This chunk describes the management of compliance and enforcement matters, which includes processes for addressing quality issues."
            }
          ],
          "proofs_to_validate": [
            "The documentation explicitly establishes processes to detect and prevent quality problems, fulfilling the requirements of the clause.",
            "The procedures outlined include identification, evaluation, reporting, and tracking of noncompliances, which are essential for quality assurance.",
            "The chunks collectively demonstrate a comprehensive approach to quality management, including screening and corrective actions.",
            "The roles and responsibilities defined in the documentation ensure accountability in managing quality issues, supporting the clause's intent.",
            "The presence of specific procedures and guidelines indicates a structured approach to quality management, aligning with the contractor's obligations."
          ],
          "accountability_lead": "Derek Overcash"
        },
        {
          "clause": "The contractor must identify, control, and correct items, services, and processes that do not meet established requirements.",
          "compliance_status": "Fully Meeting",
          "chunk_ids": [
            {
              "chunk_id": "f34febb8-dc3b-4e8c-98b1-e4ffac1e33d1",
              "chunk_content": "This procedure establishes the United Cleanup Oak Ridge LLC (UCOR) process for the identification, evaluation, reporting, and tracking of noncompliances with the U.S. Department of Energy (DOE) nuclear and criticality safety requirements enforceable under the Price-Anderson Amendments Act (PAAA) and its implementing regulations, Worker Safety and Health (WSH) requirements enforceable under 10 Code of Federal Regulations (CFR) 851, and Classified Information Security (CIS) requirements enforceable under 10 CFR 824. This procedure was developed in accordance with the guidance provided in the DOE Enforcement Process Overview issued by the Office of Enforcement.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "3",
              "reasoning": "This chunk outlines the process for identifying, evaluating, reporting, and tracking noncompliances, which directly aligns with the requirements of the clause."
            },
            {
              "chunk_id": "3ca89186-53aa-4f62-a583-be5c6584da3f",
              "chunk_content": "o identify, control, and correct items, services, and processes that do not meet established requirements.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "9",
              "reasoning": "This chunk explicitly states the requirement to identify, control, and correct noncompliant items, services, and processes, demonstrating adherence to the clause."
            },
            {
              "chunk_id": "699a0dd8-9f5e-481b-b060-1b42adc8bd56",
              "chunk_content": "Typically noncompliances are reported internally into CAMS and/or externally into NTS, as appropriate, within 20 days of the noncompliance determination by the PAAA Enforcement Coordinator.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "6",
              "reasoning": "This chunk describes the reporting process for noncompliances, which is a critical part of controlling and correcting issues that do not meet established requirements."
            },
            {
              "chunk_id": "1c13556b-9189-48b5-8688-1a8a3e80b8b5",
              "chunk_content": "The PAAA Enforcement Coordinator or Designee is responsible for submitting the report into NTS, distributing a copy of the NTS Report to relevant parties, updating the NTS concurrently with CAMS as corrective actions are identified, and coordinating closure of NTS reports with DOE OREM and the DOE Office of Enforcement.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "6",
              "reasoning": "This chunk outlines the responsibilities of the PAAA Enforcement Coordinator in managing noncompliance reports, which includes corrective actions, thus fulfilling the clause's requirements."
            },
            {
              "chunk_id": "c544dcb8-3f17-4e43-b7a0-7206c584478f",
              "chunk_content": "This table outlines various reporting thresholds for compliance violations and their corresponding explanatory notes.",
              "document_name": "procpq1610 - eDCRO_40059.pdf",
              "page_no": "13",
              "reasoning": "This chunk provides a framework for identifying and reporting compliance violations, which supports the identification and correction of noncompliant items and processes."
            }
          ],
          "proofs_to_validate": [
            "The procedure establishes a clear process for identifying, evaluating, reporting, and tracking noncompliances, which is essential for compliance with the clause.",
            "Explicit mention of the need to identify, control, and correct noncompliant items, services, and processes is made in the documentation.",
            "The reporting mechanisms described ensure that noncompliances are addressed in a timely manner, aligning with the clause's requirements.",
            "The responsibilities assigned to the PAAA Enforcement Coordinator include corrective actions, which are necessary for compliance with the established requirements.",
            "The documentation provides a comprehensive framework for compliance reporting, ensuring that all noncompliances are systematically identified and addressed."
          ],
          "accountability_lead": "PAAA Enforcement Coordinator"
        }
      ]
    }
  ]
}





extrated_clauses_10CFR = [
    {
        "id": "515884dc-1042-4b71-b22b-5e30bfc9ccd1",
        "clause": "# § 830.121 Quality Assurance Program (QAP)\n\n## Overview\nContractors conducting activities that may affect the nuclear safety of DOE nuclear facilities are required to adhere to specific Quality Assurance (QA) criteria.\n\n## Requirements for Contractors\n\n### General Obligations\n- Contractors must conduct work in accordance with the Quality Assurance criteria outlined in [§ 830.122](https://www.ecfr.gov/on/2024-04-25/title-10/section-830.122/).\n\n### Responsibilities of the Contractor\nThe contractor responsible for a DOE nuclear facility must:\n\n1. **Submit a Quality Assurance Program (QAP)**\n   - Submit a QAP to DOE for approval.\n   - The QAP will be regarded as approved 90 days after submission unless it is approved or rejected by DOE earlier.\n\n2. **Modify the QAP**\n   - Modify the QAP as directed by DOE.\n\n3. **Annual Submission of Changes**\n   - Annually submit any changes to the DOE-approved QAP for approval.\n   - Justify in the submission why the changes continue to satisfy the quality assurance requirements.\n\n4. **Conduct Work According to the QAP**\n   - Ensure that all work is conducted in accordance with the approved QAP.\n\n## QAP Content Requirements\nThe QAP must:\n\n- Describe how the quality assurance criteria of [§ 830.122](https://www.ecfr.gov/on/2024-04-25/title-10/section-830.122/) are satisfied.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "1",
            "10 CFR Part 830 Subpart A.pdf"
        ]
    },
    {
        "id": "a443cbe4-fca4-486f-97b3-bee5d4b35077",
        "clause": "# § 830.121 Quality Assurance Program (QAP)\n\n## Key Components of the Quality Assurance Program\n\n1. **Integration with Safety Management System**\n   - Integrate the quality assurance criteria with the Safety Management System.\n   - Alternatively, describe how the quality assurance criteria apply to the Safety Management System.\n\n2. **Use of Voluntary Consensus Standards**\n   - Utilize voluntary consensus standards in the development and implementation of the QAP, where practicable.\n   - Ensure consistency with contractual and regulatory requirements.\n   - Identify the standards used in the process.\n\n3. **Contractor Responsibilities**\n   - Describe how the contractor responsible for the nuclear facility ensures that subcontractors and suppliers meet the criteria outlined in [§ 830.122](https://www.ecfr.gov/on/2024-04-25/title-10/section-830.122/). \n\nThis structured approach ensures clarity and compliance within the Quality Assurance Program, promoting safety and quality in nuclear facility operations.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "1",
            "10 CFR Part 830 Subpart A.pdf"
        ]
    },
    {
        "id": "900f29a5-c617-4426-953f-4fb582581864",
        "clause": "# § 830.122 Quality Assurance Criteria\n\nThe Quality Assurance Program (QAP) must address the following management, performance, and assessment criteria:\n\n## Criterion 1 — Management/Program\n1. **Organizational Structure**\n   - Establish an organizational structure, functional responsibilities, levels of authority, and interfaces for those managing, performing, and assessing the work.\n   \n2. **Management Processes**\n   - Establish management processes, including:\n     - Planning\n     - Scheduling\n     - Providing resources for the work\n\n## Criterion 2 — Management/Personnel Training and Qualification\n1. **Personnel Training**\n   - Train and qualify personnel to be capable of performing their assigned work.\n   \n2. **Continuing Training**\n   - Provide continuing training to personnel to maintain their job proficiency.\n\n## Criterion 3 — Management/Quality Improvement\n1. **Quality Problem Detection**\n   - Establish and implement processes to detect and prevent quality problems.\n   \n2. **Control and Correction**\n   - Identify, control, and correct items, services, and processes that do not meet established requirements.\n   \n3. **Problem Cause Identification**\n   - Identify the causes of problems and work to prevent recurrence as part of correcting the problem.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "10 CFR Part 830 Subpart A.pdf",
            "2"
        ]
    },
    {
        "id": "a948cd2a-1add-4408-9895-0568fceadf81",
        "clause": "# § 830.122 Quality Assurance Criteria\n\n## Overview\nThis document outlines the quality assurance criteria necessary for effective management and performance within an organization. The criteria are divided into several key areas, each focusing on specific aspects of quality assurance.\n\n## Criteria Breakdown\n\n### Criterion 4: Management/Documents and Records\n- **Document Management**\n  - Prepare, review, approve, issue, use, and revise documents to:\n    - Prescribe processes\n    - Specify requirements\n    - Establish design\n- **Records Management**\n  - Specify, prepare, review, approve, and maintain records.\n\n### Criterion 5: Performance/Work Processes\n- **Work Consistency**\n  - Perform work consistent with:\n    - Technical standards\n    - Administrative controls\n    - Other hazard controls adopted to meet regulatory or contract requirements\n  - Use approved instructions, procedures, or other appropriate means.\n- **Item Control**\n  - Identify and control items to ensure their proper use.\n- **Maintenance**\n  - Maintain items to prevent:\n    - Damage\n    - Loss\n    - Deterioration\n- **Equipment Calibration**\n  - Calibrate and maintain equipment used for:\n    - Process monitoring\n    - Data collection\n\n### Criterion 6: Performance/Design\n- Further details on this criterion are not provided in the text.\n\n## Conclusion\nThe quality assurance criteria outlined above are essential for identifying areas needing improvement and ensuring that processes and items are managed effectively within an organization.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "10 CFR Part 830 Subpart A.pdf",
            "2"
        ]
    },
    {
        "id": "e4c250ef-a303-4173-ad13-a20ea31bfbb5",
        "clause": "# § 830.122 Quality Assurance Criteria\n\n## Design Criteria\n1. **Design Principles**\n   - Design items and processes using sound engineering/scientific principles and appropriate standards.\n   \n2. **Requirements Incorporation**\n   - Incorporate applicable requirements and design bases in design work and design changes.\n   \n3. **Design Interfaces**\n   - Identify and control design interfaces.\n   \n4. **Verification and Validation**\n   - Verify or validate the adequacy of design products using individuals or groups other than those who performed the work.\n   - Verify or validate work before approval and implementation of the design.\n\n## Performance/Procurement Criteria\n1. **Procurement Standards**\n   - Procure items and services that meet established requirements and perform as specified.\n   \n2. **Supplier Evaluation**\n   - Evaluate and select prospective suppliers based on specified criteria.\n   - Establish and implement processes to ensure that approved suppliers continue to provide acceptable items and services.\n\n## Performance/Inspection and Acceptance Testing Criteria\n1. **Inspection and Testing**\n   - Inspect and test specified items, services, and processes using established acceptance and performance criteria.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "10 CFR Part 830 Subpart A.pdf",
            "3, 2"
        ]
    },
    {
        "id": "6b77eeb5-2d8d-4c6c-9267-7e563725eeb2",
        "clause": "# § 830.122 Quality Assurance Criteria\n\n## Equipment Calibration and Maintenance\n- Calibrate and maintain equipment used for inspections and tests.\n\n## Assessment Criteria\n\n### Criterion 9 — Management Assessment\n- Ensure managers:\n  - Assess their management processes.\n  - Identify and correct problems that hinder the organization from achieving its objectives.\n\n### Criterion 10 — Independent Assessment\n1. **Planning and Conducting Assessments**\n   - Plan and conduct independent assessments to:\n     - Measure item and service quality.\n     - Measure the adequacy of work performance.\n     - Promote improvement.\n\n2. **Authority and Independence**\n   - Establish sufficient authority and freedom from line management for the group performing independent assessments.\n\n3. **Qualifications of Assessors**\n   - Ensure that individuals performing independent assessments are:\n     - Technically qualified.\n     - Knowledgeable in the areas to be assessed.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "10 CFR Part 830 Subpart A.pdf",
            "3"
        ]
    }
]
 
extrated_clauses_226 =[
    {
        "id": "6a52983a-936d-4c73-bf55-2501ec5fc7de",
        "clause": "# Contractor Assurance System \n\n## 1. Responsibilities\n- The contractor is responsible for complying with the requirements of this Contractor Requirements Document (CRD), regardless of who performs the work.\n- The contractor must flow down the requirements of this CRD to subcontractors at any tier as necessary to ensure compliance.\n- Contractors are required to:\n  - Monitor and evaluate all work performed under their contracts.\n  - Ensure that the work of subcontractors meets applicable requirements for:\n    - Environment\n    - Safety and health\n    - Quality assurance\n    - Integrated safety management\n    - Safeguards and security\n    - Cyber security\n    - Business and financial systems\n    - Emergency management\n\n## 2. Requirements\n- The contractor must establish an assurance system that includes:\n  - Assignment of management responsibilities and accountabilities.\n  - Evidence to assure both the Department of Energy (DOE) and the contractor’s management that:\n    - Work is being performed safely, securely, and in compliance with all requirements.\n    - Risks are being identified and managed.\n    - Systems of control are effective and efficient.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "9",
            "DOE_O_226_1B.pdf"
        ]
    },
    {
        "id": "642add36-581c-4125-80cb-339dd0102c3d",
        "clause": "# Contractor Assurance System\n\n## Overview\nThe Contractor Assurance System is designed to ensure the effectiveness and reliability of contractor operations. It must include several key components to maintain high standards of performance and accountability.\n\n## Key Components\nThe contractor assurance system must include the following elements:\n\n1. **Validation of Assurance System Processes**\n   - A method for validating the effectiveness of assurance system processes.\n   - Integration of:\n     - Third-party audits\n     - Peer reviews\n     - Independent assessments\n     - External certification\n   - These elements should complement, but not replace, internal assurance systems.\n\n2. **Self-Assessment and Improvement Activities**\n   - Rigorous, risk-informed, and credible self-assessment processes.\n   - Feedback and improvement activities must be:\n     - Risk-informed\n     - Formally described and documented\n     - Appropriately cover potentially high-consequence activities\n\n3. **Structured Issues Management System**\n   - A formally described and documented issues management system that:\n     - Captures program and performance deficiencies (individually and collectively).\n     - Provides for timely reporting and compensatory corrective actions when needed.\n   - The issues management process must:\n     - Categorize the significance of findings based on risk, priority, and other appropriate factors.\n     - Enable contractor management to ensure timely evaluation and correction of problems.\n\n### Higher Significance Findings\nFor issues categorized as higher significance findings, contractor management must ensure the following activities are completed and documented:\n- [Details to be provided based on specific organizational requirements or guidelines.]\n\nBy adhering to these components, the Contractor Assurance System can effectively manage risks and enhance overall performance.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "DOE_O_226_1B.pdf",
            "10, 9"
        ]
    },
    {
        "id": "c97e9ae5-64be-436b-8f37-d9547b2f52aa",
        "clause": "# Contractor Assurance System \n\nThe Contractor Assurance System is designed to ensure effective management and resolution of issues within contractor operations. The system consists of several key components:\n\n## Key Components\n\n1. **Causal Analysis**\n   - A thorough analysis of the underlying causal factors is completed.\n\n2. **Corrective Actions**\n   - Timely corrective actions are identified and implemented to address the causes of findings and prevent recurrence.\n\n3. **Effectiveness Review**\n   - After the completion of corrective actions, an effectiveness review is conducted by trained and qualified personnel to validate the effectiveness of the corrective action/plan implementation and its results in preventing recurrences.\n\n4. **Documentation and Tracking**\n   - Documentation of the analysis process and results is maintained, along with tracking to completion of plans and schedules for corrective actions and effectiveness reviews.\n\n5. **Communication**\n   - Issues and performance trends or analysis results are communicated up the contractor management chain to senior management. This communication uses a graded approach that considers hazards and risks, providing a sufficient technical basis for informed decision-making. This helps in correcting negative performance/compliance trends before they escalate into significant issues.\n\n## Conclusion\n\nThe Contractor Assurance System is a comprehensive framework that emphasizes analysis, corrective action, effectiveness review, documentation, and communication to enhance contractor performance and compliance.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "10",
            "DOE_O_226_1B.pdf"
        ]
    },
    {
        "id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809",
        "clause": "# Contractor Assurance System \n\n## Key Components\n\n1. **Timely Communication**\n   - Ensure appropriate communication with the Contracting Officer.\n   - Provide electronic access to assurance-related information.\n\n2. **Continuous Feedback and Improvement**\n   - Implement worker feedback mechanisms, such as:\n     - Employee concerns programs\n     - Telephone hotlines\n     - Employee suggestions forms\n     - Labor organization input\n   - Focus on improvements in:\n     - Work planning\n     - Hazard identification activities\n     - Lessons learned programs\n\n3. **Metrics and Targets**\n   - Establish metrics and targets to assess performance effectiveness.\n   - Benchmark key functional areas against:\n     - Other DOE contractors\n     - Industry standards\n     - Research institutions\n\n## Submission Requirements\n\n- The contractor must submit an initial description of the contractor assurance system to the Contracting Officer for DOE review and approval. This description should:\n  - Clearly define processes\n  - Outline key activities\n  - Specify accountabilities\n\n- If necessary, an implementation plan should be included that:\n  - Considers and mitigates risks\n  - Encompasses all facilities, systems, and organizational elements\n\n## Notification of Changes\n\n- Once the description is approved, the contractor must provide timely notification to the Contracting Officer regarding any significant changes to the assurance system **prior** to implementing those changes.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "DOE_O_226_1B.pdf",
            "10, 11"
        ]
    },
    {
        "id": "ee02e075-3ff2-4e5a-a7a3-ac6c009a9e48",
        "clause": "# Contractor Assurance System \n\n## Overview\nThe Contractor Assurance System is designed to ensure appropriate oversight of contractor activities. It emphasizes the importance of documentation and data availability for effective monitoring and evaluation.\n\n## Key Requirements\n\n- **Documentation and Availability**\n  - Contractor assurance system data must be:\n    - Documented\n    - Readily available to the Department of Energy (DOE)\n\n- **Analysis and Reporting**\n  - Results of assurance processes must be:\n    - Analyzed\n    - Compiled\n    - Reported to the DOE as requested by the Contracting Officer\n\n## Purpose of Reporting\nThe reporting of assurance process results serves several purposes, including:\n- Supporting contractor evaluations\n- Assisting in the review and approval of corrective action plans",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "DOE_O_226_1B.pdf",
            "11"
        ]
    }
]

extracted_clauses_414 = [
    {
        "id": "4593168d-aa2d-4088-be88-d9ecd2d4003e",
        "clause": "# Contractor Requirements Document\n\n## DOE O 414.1D CHG 2: Quality Assurance\n\n### Overview\nThe contractor is responsible for complying with the requirements outlined in this Contractor Requirements Document (CRD), regardless of who performs the work. \n\n### Responsibilities\n- **Contractor Obligations**: \n  - Ensure compliance with the CRD requirements.\n  - Flow down applicable requirements to subcontractors at any tier, as well as vendors and suppliers.\n  - Guarantee compliance and safe performance of work.\n\n### Quality Assurance Requirements\n- When conducting activities or providing items or services that may affect the safety of the Department of Energy (DOE) facilities, including those under the National Nuclear Security Administration (NNSA), the contractor must:\n  - Adhere to the quality assurance (QA) requirements of **10 C.F.R. Part 830 Subpart A**.\n  - Follow additional requirements specified in this CRD, unless the work falls under exclusions found in **10 C.F.R. § 830.2**.\n\n### Exclusions and Applicability\n- Requirements of this CRD that overlap or duplicate those of the **Nuclear Regulatory Commission (NRC)** are not applicable to:\n  - Facilities or activities subject to an NRC license (including construction authorization).\n  - Activities related to NRC regulatory authority (including design, construction, operation, deactivation, and decommissioning).\n  \n- Other requirements in this CRD may be applied as deemed appropriate by the responsible Program Office. \n\n### Conclusion\nIt is essential for contractors to understand and implement these requirements to ensure compliance and maintain safety standards in all operations related to DOE facilities.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "15",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "264bfb90-3245-4fba-9ad3-58b648c2a17e",
        "clause": "# Contractor Requirements Document\n\n## DOE O 414.1D CHG 2: Quality Assurance\n\nIn addition to the requirements set forth in this Contractor Requirements Document (CRD), Attachments 2, 3, and 4 to DOE O 414.1D are incorporated into this CRD. These attachments provide program requirements and/or information applicable to contracts in which this CRD is included.\n\n## 1. Quality Assurance Program Development and Implementation\n\nThe contractor must:\n\n- Identify and assign an individual responsible for:\n  - Authority\n  - Accountability\n  - Ensuring the development, implementation, assessment, maintenance, and improvement of the Quality Assurance Program (QAP)\n\n- Develop a QAP using a graded approach and conduct work in accordance with the approved QAP that meets the requirements of this CRD.\n\n### The QAP must:\n\n- **Describe the graded approach** used in the QAP.\n- **Implement QA criteria** as defined in:\n  - **Attachment 2**: General QA criteria\n  - **Attachment 3**: Requirements for all facilities\n  - **Attachment 4**: Requirements for nuclear facilities\n\n- **Document how the criteria/requirements are met** using the documented graded approach.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "15",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "9c361931-c7cf-42db-9336-0a0c990216a2",
        "clause": "# Contractor Requirements Document\n\n## DOE O 414.1D CHG 2: Quality Assurance\n\n### Overview\nThis document outlines the requirements for software quality assurance (QA) as per the DOE O 414.1D CHG 2. All software must meet applicable QA requirements as specified in Attachment 2, utilizing a graded approach.\n\n### Standards Compliance\n- **National or International Standards**: \n  - Use appropriate national or international consensus standards that align with contractual and regulatory requirements, as well as Secretarial Officer direction.\n  - Clearly identify which standards or parts of the standards are being utilized.\n  \n- **Addressing Gaps**: \n  - If the standards do not fully meet the Contractor Requirements Document (CRD) requirements, the gaps must be addressed in the Quality Assurance Plan (QAP).\n\n### Selection Criteria\nSelect and document the appropriate choice based on the following criteria:\n\n1. **For Hazard Category 1, 2, and 3 Nuclear Facilities**:\n   - **Existing Facilities or New Facilities**:\n     - For existing facilities or new facilities and major modifications achieving Critical Decision 1 (CD-1) prior to the issuance of the Order containing this CRD:\n       - Continue to use the consensus standard cited in the DOE-approved QAP, consistent with Secretarial Officer direction.\n   - **New Facilities and Major Modifications**:\n     - For new facilities and major modifications achieving Critical Decision 1 (CD-1) after the issuance of the Order containing this CRD:\n       - Use **ASME NQA-1-2008** with the **NQA-1a-2009 addenda** (or a later edition), which includes:\n         - Quality Assurance Requirements for Nuclear Facility Applications, Part I\n         - Applicable requirements of Part II. \n\n### Conclusion\nAdhering to these requirements ensures that all software developed for nuclear facilities meets the necessary quality assurance standards, thereby maintaining safety and compliance with regulatory expectations.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "DOE_O_414_1D.pdf",
            "15, 16"
        ]
    },
    {
        "id": "4873245b-91ed-4a52-ad7c-4383205c74c2",
        "clause": "# Contractor Requirements Document\n\n## DOE O 414.1D CHG 2: Quality Assurance\n\n### Applicable Standards\nThe following standards are relevant to the Quality Assurance requirements:\n\n1. **ASME NQA 1-2000**\n   - Quality Assurance Requirements for Nuclear Facility Applications, Part I\n   - Applicable requirements of Part II\n\n2. **ANSI/ISO/ASQ Q9001-2008**\n   - Quality Management System: Requirements\n\n3. **ANSI/ASQ Z 1.13-1999**\n   - Quality Guidelines for Research\n\n---\n\n## Quality Assurance Program Approvals and Changes\n\nThe contractor must adhere to the following requirements regarding the Quality Assurance Program (QAP):\n\n### Submission and Approval\n- **QAP Submission**: \n  - Submit a QAP to the Department of Energy (DOE) for approval within **90 days** of being awarded a DOE contract.\n  \n- **Implementation**: \n  - Implement the QAP as approved by DOE.\n\n### Annual Review\n- **Review Process**: \n  - Review the QAP annually and update as needed.\n  \n- **Reporting**: \n  - Submit a summary of the annual review of the QAP.\n  - If necessary, submit the modified QAP to the DOE approval authority.\n\n### Editorial Changes\n- **Approval Exemption**: \n  - Editorial changes that do not reduce or change commitments do not require approval.\n\n### Approval Timeline\n- **Approval Period**: \n  - A QAP is regarded as approved by DOE **90 calendar days** after receipt, unless it is approved or rejected by DOE at an earlier date.\n  \n- **Receipt Acknowledgment**: \n  - Receipt includes acknowledgment by the receiving organization.\n  - Every official submittal to DOE restarts the **90-day clock**.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "17, 16",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "2e019233-00c5-4dff-8a6a-6d044f79249b",
        "clause": "# Contractor Requirements Document\n\n## DOE O 414.1D CHG 2: Quality Assurance\n\n### Subcontractor, Vendor, and Supplier Activities\n\n- For subcontractor, vendor, and supplier activities that are not governed by the contractor’s DOE-approved Quality Assurance Program (QAP):\n  - Evaluate their program to ensure it meets applicable Quality Assurance (QA) requirements.\n\n### Reference\n\n- ![Image Reference](http://DOE_O_414_1D.pdf/Figure_M_2.png)",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "DOE_O_414_1D.pdf",
            "17, 18"
        ]
    },
    {
        "id": "162eed6f-13b6-42fb-9b22-a28bc04e18e8",
        "clause": "# Quality Assurance Criteria\n\nThis document provides information and requirements associated with DOE O 414.1D and is applicable to contracts in which the associated CRD (Attachment 1) is inserted.\n\n## 1. Criterion 1— Management/Program\n- Establish an organizational structure, functional responsibilities, levels of authority, and interfaces for those managing, performing, and assessing the work.\n- Establish management processes, including:\n  - Planning\n  - Scheduling\n  - Providing resources for the work\n\n## 2. Criterion 2— Management/Personnel Training and Qualification\n- Train and qualify personnel to be capable of performing their assigned work.\n- Provide continuing training to personnel to maintain their job proficiency.\n\n## 3. Criterion 3— Management/Quality Improvement\n- Establish and implement processes to detect and prevent quality problems.\n- Identify, control, and correct items, services, and processes that do not meet established requirements.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "19",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "bd033bfa-a5a8-4134-b9b4-2f11beb4f7a2",
        "clause": "# Quality Assurance Criteria\n\n## 3. Criterion 3— Management/Quality Improvement\n- **Identify Causes of Problems**\n  - Include prevention of recurrence as part of corrective action planning.\n  \n- **Review Quality Information**\n  - Analyze item characteristics, process implementation, and other quality-related information to identify items, services, and processes needing improvement.\n\n## 4. Criterion 4— Management/Documents and Records\n- **Document Management**\n  - Prepare, review, approve, issue, use, and revise documents to:\n    - Prescribe processes\n    - Specify requirements\n    - Establish design\n  \n- **Record Maintenance**\n  - Specify, prepare, review, approve, and maintain records.\n\n## 5. Criterion 5— Performance/Work Processes\n- **Work Performance**\n  - Perform work consistent with:\n    - Technical standards\n    - Administrative controls\n    - Other hazard controls adopted to meet regulatory or contract requirements using approved instructions, procedures, or other appropriate means.\n  \n- **Item Control**\n  - Identify and control items to ensure proper use.\n  \n- **Maintenance**\n  - Maintain items to prevent damage, loss, or deterioration.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "19",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "e5c0a755-48b3-42ce-a143-34e99db14cc7",
        "clause": "# Quality Assurance Criteria\n\n## 5. Criterion 5— Performance/Work Processes\n- Calibrate and maintain equipment used for process monitoring or data collection.\n\n## 6. Criterion 6— Performance/Design\n- **a.** Design items and processes using sound engineering/scientific principles and appropriate standards.\n- **b.** Incorporate applicable requirements and design bases in design work and design changes.\n- **c.** Identify and control design interfaces.\n- **d.** Verify or validate the adequacy of design products using individuals or groups other than those who performed the work.\n- **e.** Verify or validate work before approval and implementation of the design.\n\n## 7. Criterion 7— Performance/Procurement\n- **a.** Procure items and services that meet established requirements and perform as specified.\n- **b.** Evaluate and select prospective suppliers on the basis of specified criteria.\n- **c.** Establish and implement processes to ensure that approved suppliers continue to provide acceptable items and services.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "DOE_O_414_1D.pdf",
            "20"
        ]
    },
    {
        "id": "c44ba3f6-1817-458f-813b-fa23c3ceaf0b",
        "clause": "# Quality Assurance Criteria\n\n## Criterion 7 — Performance/Procurement\n\n## Criterion 8 — Performance/Inspection and Acceptance Testing\n- Inspect and test specified items, services, and processes using established acceptance and performance criteria.\n- Calibrate and maintain equipment used for inspections and tests.\n\n## Criterion 9 — Assessment/Management Assessment\n- Ensure that managers assess their management processes.\n- Identify and correct problems that hinder the organization from achieving its objectives.\n\n## Criterion 10 — Assessment/Independent Assessment\n- Plan and conduct independent assessments to:\n  - Measure item and service quality.\n  - Measure the adequacy of work performance.\n  - Promote improvement.\n- Establish sufficient authority and freedom from line management for independent assessment teams.\n- Ensure that individuals performing independent assessments are technically qualified and knowledgeable in the areas to be assessed.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "DOE_O_414_1D.pdf",
            "20"
        ]
    },
    {
        "id": "0eb1ec1e-7650-42bb-9395-2f01292bb30b",
        "clause": "# SUSPECT/COUNTERFEIT ITEMS PREVENTION\n\nThis document provides information and requirements associated with DOE O 414.1D and is applicable to contracts in which the associated CRD (Attachment 1) is inserted.\n\n## 1. PURPOSE\n\nThe purpose of this document is to set forth requirements for the Department of Energy (DOE) and its contractor organizations. These requirements are part of their Quality Assurance Programs (QAPs) and aim to:\n\n- Ensure items and services meet specified requirements.\n- Prevent the entry of Suspect/Counterfeit Items (S/CIs) into the DOE supply chain.\n- Ensure detection, control, reporting, and disposition of S/CIs.\n\n## 2. REQUIREMENTS\n\nThe organization's QAP must include the following:\n\na. **S/CI Oversight and Prevention Process**  \n   - Establish a process that is commensurate with the facility/activity hazards and mission impact.\n\nb. **Responsible Position Identification**  \n   - Identify the position responsible for S/CI activities and designate a point of contact with the Office of Health, Safety, and Security.\n\nc. **Training and Information**  \n   - Provide training and inform managers, supervisors, and workers on S/CI processes and controls, including:\n     - Prevention\n     - Detection\n     - Disposition of S/CIs.",
        "type_of_clause": "Consultant_Clause",
        "independent": "false",
        "reference": [
            "21",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "d61f49d5-0678-4908-980b-b8e5b40ffe30",
        "clause": "# SUSPECT/COUNTERFEIT ITEMS PREVENTION\n\n## Introduction\nPreventing the introduction of suspect or counterfeit items (S/CIs) into Department of Energy (DOE) work is crucial for maintaining safety and compliance. The following guidelines outline the necessary steps to mitigate risks associated with S/CIs.\n\n## Prevention Strategies\nTo effectively prevent the introduction of S/CIs, the following strategies should be implemented:\n\n1. **Engineering Involvement**\n   - Involve engineering in:\n     - Development of procurement specifications\n     - Inspection and testing processes\n     - Maintenance, replacement, or modification of equipment\n\n2. **Technical and Quality Assurance Requirements**\n   - Identify and include technical and QA requirements in procurement specifications.\n\n3. **Compliance Acceptance**\n   - Accept only those items that:\n     - Comply with procurement specifications\n     - Meet consensus standards\n     - Align with commonly accepted industry practices\n\n4. **Inventory Inspection**\n   - Regularly inspect inventory and storage areas to:\n     - Identify S/CIs\n     - Control S/CIs\n     - Properly dispose of S/CIs\n\n## Inspection and Disposition Processes\nInclude processes for the following:\n\n- **Inspection and Identification**\n  - Establish procedures for inspecting, identifying, evaluating, and disposing of S/CIs that have been installed in:\n    - Safety applications\n    - Other applications that create potential hazards\n\n- **Supporting Engineering Evaluations**\n  - Utilize engineering evaluations to support the acceptance of installed S/CIs.\n  - Implement marking strategies to prevent future reuse of S/CIs.\n\n## Engineering Evaluations\nConduct engineering evaluations for the disposition of identified S/CIs, particularly those installed in:\n\n- Safety applications/systems\n- Applications that pose potential hazards\n\n### Evaluation Considerations\nEvaluations must take into account:\n\n- Potential risks to:\n  - The environment\n  - The public\n  - Workers\n\n- Cost/benefit impact\n- Schedule for replacement (if required)\n\nBy following these guidelines, organizations can significantly reduce the risk of S/CIs affecting DOE work and ensure a safer working environment.",
        "type_of_clause": "Consultant_Clause",
        "independent": "true",
        "reference": [
            "21, 22",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "51668e33-97c7-4bbb-ab49-8d0a65fb36ee",
        "clause": "# SUSPECT/COUNTERFEIT ITEMS PREVENTION\n\n## Evaluation of S/CIs\n- Perform evaluations to determine if Suspect/Counterfeit Items (S/CIs) installed in non-safety applications pose potential safety hazards or can remain in place.\n- Disposition S/CIs identified during routine maintenance and/or inspections to prevent future use in these applications.\n\n## Reporting Requirements\n- Report to the DOE Inspector General as per the guidelines in paragraph 3 below and DOE O 221.1, which covers Reporting Fraud, Waste, and Abuse to the Office of Inspector General (current version).\n\n## Information Management\n- Collect, maintain, disseminate, and utilize the most accurate and up-to-date information on S/CIs and suppliers.\n  - Sources for this information can be found on the [DOE S/CI website](http://www.hss.energy.gov/sesa/corporatesafety/sci/).\n\n## Trend Analysis\n- Conduct trend analyses to improve the S/CI prevention process.\n\n## Definition of Safety Applications\n- Safety applications are defined as those whose failure could adversely affect:\n  - The environment\n  - The safety or health of the public or workers\n- This term includes safety systems in nuclear facilities (refer to 10 C.F.R. § 830.3).\n\n## Additional Notes\n- DOE O 210.2, DOE Corporate Operating Experience Program (current version), requires:\n  - Review of existing lessons learned reports\n  - Submission of new lessons learned reports to enhance the S/CI prevention process.",
        "type_of_clause": "Consultant_Clause",
        "independent": "true",
        "reference": [
            "21, 22",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "ed0ca36c-ee6c-426b-92c5-2f2a879b578e",
        "clause": "# SUSPECT/COUNTERFEIT ITEMS PREVENTION\n\n## 1. Inspector General\n- **Contact the DOE Inspector General (IG)** before destroying or disposing of Suspect/Counterfeit Items (S/CIs) and corresponding documentation.\n- This allows the IG to determine whether the items and documentation need to be retained for criminal investigation or litigation.\n\n## 2. Occurrence Reporting\n- S/CIs must be reported in accordance with **DOE O 232.2**, which covers the Occurrence Reporting and Processing of Operations Information.\n- Ensure compliance with the current version of this directive.",
        "type_of_clause": "Consultant_Clause",
        "independent": "true",
        "reference": [
            "22",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "a3dc1a10-ea4b-4a81-8eff-3c565890a082",
        "clause": "# Safety Software Quality Assurance Requirements for Nuclear Facilities\n\nThis document provides information and requirements associated with DOE O 414.1D and is applicable to contracts in which the associated CRD (Attachment 1) is inserted.\n\n## 1. Purpose\n\n- Prescribe the safety software quality assurance (SSQA) requirements for DOE nuclear facilities.\n- Note that software, other than safety software as defined in this Order, is not subject to the requirements in this Attachment.\n\n## 2. Requirements\n\n- Safety software must be acquired, developed, and implemented using:\n  - **ASME NQA-1-2008** with the **NQA-1a-2009** addenda (or a later edition).\n  - Quality Assurance Requirements for Nuclear Facility Applications, Part I and Subpart 2.7.\n  - Other national or international consensus standards that provide an equivalent level of quality assurance requirements as NQA-1-2008.\n\n- DOE-approved Quality Assurance Plans (QAPs) applicable to safety software based on requirements from DOE O 414.1C are acceptable.\n\n- The standards used must be specified by the user and approved by the designated DOE approval authority.\n\n### Management of Safety Software\n\nManagement of safety software must include the following elements:\n- [Further details on management elements would be listed here, if provided.] \n\n---\n\nThis structured format enhances readability and clarity, making it easier to understand the safety software quality assurance requirements for nuclear facilities.",
        "type_of_clause": "Consultant_Clause",
        "independent": "true",
        "reference": [
            "23",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "10833c56-c48e-4660-8fea-901bf9b6f217",
        "clause": "# Safety Software Quality Assurance Requirements for Nuclear Facilities\n\n## 2. Requirements\n\n1. **Involvement of Facility Design Authority**\n   - Engage the facility design authority in the following processes:\n     - Identification of requirements\n     - Specification of requirements\n     - Acquisition of software\n     - Design and development\n     - Verification and validation (including inspection and testing)\n     - Configuration management\n     - Maintenance\n     - Retirement of software\n\n2. **Safety Software Inventory**\n   - Identify, document, control, and maintain a safety software inventory. Each inventory entry must include, at a minimum:\n     - Software description\n     - Software name\n     - Version identifier\n     - Safety software designation (e.g., safety system software, safety and hazard analysis software, design software, safety management and administrative controls software)\n     - Grade level designation\n     - Specific nuclear facility application used\n     - Responsible individual\n\n3. **Grading Levels for Safety Software**\n   - Establish and document grading levels for safety software using a graded approach.\n   - Grading levels must be submitted to and approved by the responsible DOE approval authority.",
        "type_of_clause": "Consultant_Clause",
        "independent": "true",
        "reference": [
            "23",
            "DOE_O_414_1D.pdf"
        ]
    },
    {
        "id": "6968b95e-d65d-44df-a24a-24cfc3d349c5",
        "clause": "# Safety Software Quality Assurance Requirements for Nuclear Facilities\n\n## 2. Requirements\n\n### Example\n- Software used solely for consequence assessment purposes in establishing the technical basis of an emergency program or during emergency response is **not** considered safety software.\n\n### SSQA Work Activities\nUsing the consensus standard selected and the grading levels established and approved, select and implement applicable Software Safety Quality Assurance (SSQA) work activities from the list below:\n\n1. **Software Project Management and Quality Planning**\n2. **Software Risk Management**\n3. **Software Configuration Management**\n4. **Procurement and Supplier Management**\n5. **Software Requirements Identification and Management**\n6. **Software Design and Implementation**\n7. **Software Safety Analysis and Safety Design Methods**\n8. **Software Verification and Validation**\n9. **Problem Reporting and Corrective Action**\n10. **Training of Personnel in the Design, Development, Use, and Evaluation of Safety Software**",
        "type_of_clause": "Consultant_Clause",
        "independent": "true",
        "reference": [
            "23, 24",
            "DOE_O_414_1D.pdf"
        ]
    }
]


OUTPUT_CLAUSES_FINAL = [
        {
            "id": "c8a0d2ef-3eeb-402d-897b-ae69943fb885",
            "clause": "The contractor must establish an assurance system that includes assignment of management responsibilities and accountabilities and provides evidence to assure both the Department of Energy’s (DOE) and the contractor’s management that work is being performed safely, securely, and in compliance with all requirements; risks are being identified and managed; and that the systems of control are effective and efficient.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "9",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "6a52983a-936d-4c73-bf55-2501ec5fc7de"
        },
        {
            "id": "7855420e-0dda-45aa-bfd7-a37c4a8e5a49",
            "clause": "Rigorous, risk-informed, and credible self-assessment and feedback and improvement activities. Assessment programs must be risk-informed, formally described and documented, and appropriately cover potentially high consequence activities.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 9",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "642add36-581c-4125-80cb-339dd0102c3d"
        },
        {
            "id": "25cdd6a6-918c-4aab-976d-49bb3102f60e",
            "clause": "A structured issues management system that is formally described and documented and that: Captures program and performance deficiencies (individually and collectively) in systems that provide for timely reporting and taking compensatory corrective actions when needed.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 9",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "642add36-581c-4125-80cb-339dd0102c3d"
        },
        {
            "id": "b5999b82-7907-4d3f-8cc7-bff33c4ffe33",
            "clause": "Contains an issues management process that is capable of categorizing the significance of findings based on risk and priority and other appropriate factors that enables contractor management to ensure that problems are evaluated and corrected on a timely basis.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 9",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "642add36-581c-4125-80cb-339dd0102c3d"
        },
        {
            "id": "7e29ac57-17fd-47ba-9166-a8753bb98b12",
            "clause": "A thorough analysis of the underlying causal factors is completed;",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "c97e9ae5-64be-436b-8f37-d9547b2f52aa"
        },
        {
            "id": "aef3a606-9f19-444b-bbd8-55672a5ada79",
            "clause": "After completion of a corrective action or a set of corrective actions, an effectiveness review is conducted using trained and qualified personnel that can validate the effectiveness of corrective action/plan implementation and results in preventing recurrences;",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "c97e9ae5-64be-436b-8f37-d9547b2f52aa"
        },
        {
            "id": "e81538e6-99a9-45dd-b52d-66b0bc5feb80",
            "clause": "Documentation of the analysis process and results described in (1) above, and maintenance and tracking to completion of plans and schedules for the corrective actions and effectiveness reviews described in (2) and (3) above in a readily accessible system;",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "c97e9ae5-64be-436b-8f37-d9547b2f52aa"
        },
        {
            "id": "04364ffe-e180-4734-a28d-438bdaf09fb3",
            "clause": "Communicates issues and performance trends or analysis results up the contractor management chain to senior management using a graded approach that considers hazards and risks and provides sufficient technical basis to allow managers to make informed decisions and correct negative performance/compliance trends before they become significant issues.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "c97e9ae5-64be-436b-8f37-d9547b2f52aa"
        },
        {
            "id": "1808f19f-e6a9-459a-8aab-cae3cb829f5a",
            "clause": "Timely and appropriate communication to the Contracting Officer, including electronic access of assurance-related information.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809"
        },
        {
            "id": "fb560a88-c6da-4a0b-a857-163f373c6171",
            "clause": "Continuous feedback and improvement, including worker feedback mechanisms (e.g., employee concerns programs, telephone hotlines, employee suggestions forms, labor organization input), improvements in work planning and hazard identification activities, and lessons learned programs.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809"
        },
        {
            "id": "503a8d73-a96d-450b-82fa-d9b4a7d56927",
            "clause": "Metrics and targets to assess the effectiveness of performance, including benchmarking of key functional areas with other DOE contractors, industry, and research institutions.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809"
        },
        {
            "id": "51224f63-2894-4f8d-91de-494e91fa335b",
            "clause": "The contractor must submit an initial contractor assurance system description to the Contracting Officer for DOE review and approval.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809"
        },
        {
            "id": "eebb58fb-cfab-4da4-8870-ef7eaff14302",
            "clause": "An implementation plan that considers and mitigates risks should also be submitted if needed and should encompass all facilities, systems, and organization elements.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809"
        },
        {
            "id": "ab861d18-42ae-455e-b6bc-be527f109850",
            "clause": "Once the description is approved, timely notification must be made to the Contracting Officer of significant assurance system changes prior to the changes being made.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "10, 11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "85ee7783-65e8-4f0b-a5bd-1c3fa1c73809"
        },
        {
            "id": "a29ba0ff-a994-44fc-85b9-9288e356cc73",
            "clause": "contractor assurance system data must be documented and readily available to DOE.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "ee02e075-3ff2-4e5a-a7a3-ac6c009a9e48"
        },
        {
            "id": "3d303cef-81d7-487a-9b05-4d88c99a7a33",
            "clause": "Results of assurance processes must be analyzed, compiled, and reported to DOE as requested by the Contracting Officer.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "11",
                "File Name": "DOE_O_226_1B"
            },
            "chunk_id": "ee02e075-3ff2-4e5a-a7a3-ac6c009a9e48"
        },
        {
            "id": "07c59721-5c7f-4eaa-b1fe-a578f5a554ad",
            "clause": "Contractors must monitor and evaluate all work performed under their contracts, including the work of subcontractors, to ensure work performance meets the applicable requirements for environment, safety, and health, including quality assurance and integrated safety management; safeguards and security; cyber security; business and financial systems; and emergency management.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "18",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6a52983a-936d-4c73-bf55-2501ec5fc7de"
        },
        {
            "id": "d70bfe9a-d7e6-415a-b8d1-295c18af77b6",
            "clause": "A method for validating the effectiveness of assurance system processes. Third party audits, peer reviews, independent assessments, and external certification may be used and integrated into the contractor’s assurance system to complement, but not replace, internal assurance systems.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "642add36-581c-4125-80cb-339dd0102c3d"
        },
        {
            "id": "6c0842ae-6034-4772-a64f-fdfd7f543048",
            "clause": "The contractor must identify and assign an individual to have responsibility, authority, and accountability to ensure the development, implementation, assessment, maintenance, and improvement of the QAP.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "264bfb90-3245-4fba-9ad3-58b648c2a17e"
        },
        {
            "id": "59ec8273-241f-4ec3-b000-f2c580195ef6",
            "clause": "The QAP must do the following: a. Describe the graded approach used in the QAP.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "264bfb90-3245-4fba-9ad3-58b648c2a17e"
        },
        {
            "id": "62c2c16d-aedd-4e79-be70-80922b088a21",
            "clause": "Implement QA criteria as defined in Attachment 2, as well as the requirements in Attachment 3 for all facilities, and the requirements in Attachment 4 for nuclear facilities, and describe how the criteria/requirements are met, using the documented graded approach.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "264bfb90-3245-4fba-9ad3-58b648c2a17e"
        },
        {
            "id": "bd8d4ec7-fdbb-4e15-97ab-541df397937d",
            "clause": "This requires that all software meet applicable QA requirements in Attachment 2, using a graded approach.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15, 16",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "9c361931-c7cf-42db-9336-0a0c990216a2"
        },
        {
            "id": "374a1872-1243-4c55-992b-3124f58c5f30",
            "clause": "Clearly identify which standards, or parts of the standards, are used.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15, 16",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "9c361931-c7cf-42db-9336-0a0c990216a2"
        },
        {
            "id": "38f20d06-5f78-4f01-ae12-3beee41e55aa",
            "clause": "When standards do not fully address the CRD requirements, the gaps must be addressed in the QAP.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15, 16",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "9c361931-c7cf-42db-9336-0a0c990216a2"
        },
        {
            "id": "129625ff-3aec-41c9-9220-17fe0caa7c02",
            "clause": "For Hazard Category 1, 2 and 3 nuclear facilities: Existing facilities, or new facilities and major modifications to existing facilities achieving Critical Decision 1 (CD-1) prior to the issuance of the Order containing this CRD, continue to use the consensus standard cited in the DOE-approved QAP consistent with Secretarial Officer direction.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15, 16",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "9c361931-c7cf-42db-9336-0a0c990216a2"
        },
        {
            "id": "ce59d674-ac2e-48f7-adf1-d87655a0704c",
            "clause": "New facilities and major modifications to existing facilities achieving Critical Decision 1 (CD-1) after the Order containing this CRD has been issued use ASME NQA-1-2008 with the NQA-1a-2009 addenda (or a later edition), Quality Assurance Requirements for Nuclear Facility Applications, Part I and applicable requirements of Part II.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "15, 16",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "9c361931-c7cf-42db-9336-0a0c990216a2"
        },
        {
            "id": "dbe90c4e-5508-4e6b-a9c6-a77fefe1bfd9",
            "clause": "The QAP must document how this consensus standard is (or a set of consensus standards are) used, as well as how they are equivalent to the consensus standard listed in 1.c.(1).(b).",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "16",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "4de06840-e1ff-4be9-a3c5-38aba3a22d92"
        },
        {
            "id": "45b6876f-7f4e-426e-8bb0-295a9ab72e0c",
            "clause": "For other activities and facilities (e.g., less than hazard category 3, non-nuclear, or chemically hazardous) use in whole or in part appropriate standards.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "16",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "4de06840-e1ff-4be9-a3c5-38aba3a22d92"
        },
        {
            "id": "ca89acac-06d0-44e2-b292-a45f1bfbcdfb",
            "clause": "Implement the QAP as approved by DOE.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "17",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "4873245b-91ed-4a52-ad7c-4383205c74c2"
        },
        {
            "id": "7c88fa0c-93c3-4fd5-a944-37cc333aab76",
            "clause": "Regard a QAP as approved by DOE, 90 calendar days after receipt by DOE, unless approved or rejected by DOE at an earlier date.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "17",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "4873245b-91ed-4a52-ad7c-4383205c74c2"
        },
        {
            "id": "5b3e2237-8cdb-477e-9e4f-3d02e6d94720",
            "clause": "Establish and implement processes to ensure that approved suppliers continue to provide acceptable items and services.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "b59e478c-cc77-4834-ba89-8ca8486dfed2",
            "clause": "Ensure persons who perform independent assessments are technically qualified and knowledgeable in the areas to be assessed.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "c44ba3f6-1817-458f-813b-fa23c3ceaf0b"
        },
        {
            "id": "48e19e90-cc36-4115-9424-fa3486fe6e50",
            "clause": "Establish sufficient authority and freedom from line management for independent assessment teams.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "293ecc66-80dd-4089-b0c7-26216efc4c98"
        },
        {
            "id": "f08ad051-b125-45d8-8822-43a09403d1c0",
            "clause": "Include a S/CI oversight and prevention process commensurate with the facility/activity hazards and mission impact.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "0eb1ec1e-7650-42bb-9395-2f01292bb30b"
        },
        {
            "id": "0ce0eb27-9ab3-420c-8cc4-d5dfad55c66d",
            "clause": "Identify the position responsible for S/CI activities and for serving as a point of contact with the Office of Health, Safety, and Security.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "0eb1ec1e-7650-42bb-9395-2f01292bb30b"
        },
        {
            "id": "fda6b42c-b1d3-4558-9c06-9d32133fb6c0",
            "clause": "Provide for training and informing managers, supervisors, and workers on S/CI processes and controls (including prevention, detection, and disposition of S/CIs).",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "0eb1ec1e-7650-42bb-9395-2f01292bb30b"
        },
        {
            "id": "c6e40411-42ab-4fcc-856e-c1b3b81459f4",
            "clause": "Prevent introduction of S/CIs into DOE work by— (1) engineering involvement: (a) in the development of procurement specifications; (b) during inspection and testing; and (c) when maintaining, replacing, or modifying equipment; (2) identifying and placing technical and QA requirements in procurement specifications; (3) accepting only those items that comply with procurement specifications, consensus standards, and commonly accepted industry practices; and (4) inspecting inventory and storage areas to identify, control, and disposition for S/CIs.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21, 22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "d61f49d5-0678-4908-980b-b8e5b40ffe30"
        },
        {
            "id": "01f07693-086b-4180-bf86-b8bc13c179ec",
            "clause": "Include processes for inspection, identification, evaluation, and disposition of S/CIs that have been installed in safety applications and other applications that create potential hazards. Also address the use of supporting engineering evaluations for acceptance of installed S/CI as well as marking to prevent future reuse.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21, 22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "d61f49d5-0678-4908-980b-b8e5b40ffe30"
        },
        {
            "id": "ea0d82eb-9a01-425f-a2dc-db6b08a80f38",
            "clause": "Conduct engineering evaluations to be used in the disposition of identified S/CIs installed in safety applications/systems or in applications that create potential hazards. Evaluations must consider potential risks to the environment, the public and workers along with a cost/benefit impact, and a schedule for replacement (if required).",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21, 22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "d61f49d5-0678-4908-980b-b8e5b40ffe30"
        },
        {
            "id": "da72a715-f0e9-4658-9f74-96088a9ddc2c",
            "clause": "Perform the evaluation to determine whether S/CIs installed in non-safety applications pose potential safety hazards or may remain in place.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21, 22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "51668e33-97c7-4bbb-ab49-8d0a65fb36ee"
        },
        {
            "id": "4010c684-c54a-4c9f-b949-6c98df69e3bc",
            "clause": "Disposition S/CIs identified during routine maintenance and/or inspections to prevent future use in these applications.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21, 22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "51668e33-97c7-4bbb-ab49-8d0a65fb36ee"
        },
        {
            "id": "317ed64f-a938-43de-81af-d07d51fbf389",
            "clause": "Collect, maintain, disseminate, and use the most accurate, up to date information on S/CIs and suppliers.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21, 22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "51668e33-97c7-4bbb-ab49-8d0a65fb36ee"
        },
        {
            "id": "27ebb209-0245-45be-ac99-d5c9eb2bdada",
            "clause": "Conduct trend analyses for use in improving the S/CI prevention process.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "21, 22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "51668e33-97c7-4bbb-ab49-8d0a65fb36ee"
        },
        {
            "id": "9e7f972b-69ba-4570-9acc-a7d9da6bdee5",
            "clause": "Contact the DOE Inspector General (IG), before destroying or disposing of S/CIs and corresponding documentation, to allow the IG to determine whether the items and documentation need to be retained for criminal investigation or litigation.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "ed0ca36c-ee6c-426b-92c5-2f2a879b578e"
        },
        {
            "id": "32cd0c49-94be-40f6-a12b-141749dedb4b",
            "clause": "S/CIs must be reported in accordance with DOE O 232.2, Occurrence Reporting and Processing of Operations Information, current version.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "22",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "ed0ca36c-ee6c-426b-92c5-2f2a879b578e"
        },
        {
            "id": "f3855872-fef6-4ed6-bf62-baa5934875c9",
            "clause": "Safety software must be acquired, developed and implemented using ASME NQA-1-2008 with the NQA-1a-2009 addenda (or a later edition), Quality Assurance Requirements for Nuclear Facility Applications, Part I and Subpart 2.7, or other national or international consensus standards that provide an equivalent level of quality assurance requirements as NQA-1-2008.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "a3dc1a10-ea4b-4a81-8eff-3c565890a082"
        },
        {
            "id": "3741dff9-67be-4203-a55e-8593117bf11e",
            "clause": "The standards used must be specified by the user and approved by the designated DOE approval authority.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "a3dc1a10-ea4b-4a81-8eff-3c565890a082"
        },
        {
            "id": "a130dc19-d3d6-4a86-b558-162acae78cf7",
            "clause": "Involve the facility design authority, as applicable, in: the identification of; requirements specification; acquisition; design; development; verification and validation (including inspection and testing); configuration management; maintenance; and, retirement.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "10833c56-c48e-4660-8fea-901bf9b6f217"
        },
        {
            "id": "d88826a2-ced2-44a7-bc9d-c7dfbc93361f",
            "clause": "Identify, document, control and maintain safety software inventory. The inventory entries must include at a minimum the following: software description; software name; version identifier; safety software designation (e.g., safety system software, safety and hazard analysis software and design software, safety management and administrative controls software); grade level designation; specific nuclear facility application used; and, the responsible individual.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "10833c56-c48e-4660-8fea-901bf9b6f217"
        },
        {
            "id": "835573e4-0bc7-4568-95e9-0dd1e5c0ad7c",
            "clause": "Establish and document grading levels for safety software using the graded approach. Grading levels must be submitted to and approved by the responsible DOE approval authority.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "10833c56-c48e-4660-8fea-901bf9b6f217"
        },
        {
            "id": "ec445ef4-9d8f-4f11-ba98-80b646e3102e",
            "clause": "Using the consensus standard selected and the grading levels established and approved above, select and implement applicable SSQA work activities from the list below.",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "e2187fdb-8ed5-41db-9308-5fd5071fefc2",
            "clause": "Software project management and quality planning",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "317583af-d8fe-4375-acb3-883e3fb9c9c2",
            "clause": "Software risk management",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "1f5906e8-2adf-4aab-b808-04340099dc38",
            "clause": "Software configuration management",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "32705f89-cfbd-4ace-94fa-cd7a09896c78",
            "clause": "Procurement and supplier management",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "b41bfed6-11e9-4e3b-ae45-4c797ca1d46a",
            "clause": "Software requirements identification and management",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "3945d542-a8af-44b5-ba96-ac12b8a26e8a",
            "clause": "Software design and implementation",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "ed94fa16-42b0-4600-801f-7adf31c77169",
            "clause": "Software safety analysis and safety design methods",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "8a92df60-695e-4f21-847b-d5cf198dd08c",
            "clause": "Software verification and validation",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "3c00a3f7-bf41-4c38-b5db-6d2884dadc60",
            "clause": "Problem reporting and corrective action",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "23c881ef-3e83-4343-960a-cf9c359e71bc",
            "clause": "Training of personnel in the design, development, use, and evaluation of safety software",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "23, 24",
                "File Name": "DOE_O_414_1D"
            },
            "chunk_id": "6968b95e-d65d-44df-a24a-24cfc3d349c5"
        },
        {
            "id": "766fc723-b77e-4753-a2fe-c8d655a393a5",
            "clause": "Submit a QAP to DOE for approval within 90 days of being awarded a DOE contract.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "17",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "1",
                "File Name": "10 CFR Part 830 Subpart A."
            }
             ],
            "chunk_id": "4873245b-91ed-4a52-ad7c-4383205c74c2"
        },
        {
            "id": "6a35b0ea-e5c7-4837-8f4a-99f12d98bd65",
            "clause": "Review the QAP annually, and update as needed. Submit a summary of the annual review of the QAP and, if necessary, also submit the modified QAP to the DOE approval authority.",
            "type_of_clause": "Consultant_Clause",
            "references":[ {
                "Page No": "17",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "1",
                "File Name": "10 CFR Part 830 Subpart A."
            }
           ],
            "chunk_id": "4873245b-91ed-4a52-ad7c-4383205c74c2"
        },
        {
            "id": "20649bfc-d26f-41e3-8e7d-67e0f78db7b6",
            "clause": "The contractor, using a graded approach, must develop a QAP and conduct work in accordance with the approved QAP that meets the requirements of this CRD.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "15",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "1",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "264bfb90-3245-4fba-9ad3-58b648c2a17e"
        },
        {
            "id": "1fba9b73-a62c-41f5-9501-e08b60cf113c",
            "clause": "The contractor must conduct work in accordance with the quality assurance (QA) requirements of 10 C.F.R. Part 830 Subpart A and the additional requirements of this CRD.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "15",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "1",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "4593168d-aa2d-4088-be88-d9ecd2d4003e"
        },
        {
            "id": "e4c15be1-9bf6-462c-9f82-906f18d7373e",
            "clause": "Use appropriate national or international consensus standards consistent with contractual and regulatory requirements, and Secretarial Officer direction.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "15, 16",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "1",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "9c361931-c7cf-42db-9336-0a0c990216a2"
        },
        {
            "id": "6ccc42ac-c0c1-4662-a739-fe8dfe84e49b",
            "clause": "Establish an organizational structure, functional responsibilities, levels of authority, and interfaces for those managing, performing, and assessing the work.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "162eed6f-13b6-42fb-9b22-a28bc04e18e8"
        },
        {
            "id": "a38b72ee-5012-4816-b3b1-8e0ae38c0189",
            "clause": "Establish management processes, including planning, scheduling, and providing resources for the work.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "162eed6f-13b6-42fb-9b22-a28bc04e18e8"
        },
        {
            "id": "9ad57d10-f8e7-4f3e-af8f-bfb8da39fa8d",
            "clause": "Train and qualify personnel to be capable of performing their assigned work.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "162eed6f-13b6-42fb-9b22-a28bc04e18e8"
        },
        {
            "id": "451a7577-2d96-4087-ad18-4a8f755b96b5",
            "clause": "Provide continuing training to personnel to maintain their job proficiency.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "162eed6f-13b6-42fb-9b22-a28bc04e18e8"
        },
        {
            "id": "6f077bdb-2e8d-4fbb-aa03-818db5bc25df",
            "clause": "Establish and implement processes to detect and prevent quality problems.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "162eed6f-13b6-42fb-9b22-a28bc04e18e8"
        },
        {
            "id": "658ed930-a102-4b22-98f4-860d6a7e1cab",
            "clause": "Identify, control, and correct items, services, and processes that do not meet established requirements.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "162eed6f-13b6-42fb-9b22-a28bc04e18e8"
        },
        {
            "id": "732887ca-3921-4c07-9c99-c34f136290af",
            "clause": "Timely corrective actions that will address the cause(s) of the findings and prevent recurrence are identified and implemented;",
            "type_of_clause": "Consultant_Clause",
            "references": {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            },
            "chunk_id": "c97e9ae5-64be-436b-8f37-d9547b2f52aa"
        },
        {
            "id": "f4180b0b-b3fc-4b74-bef0-c78525596bc7",
            "clause": "Review item characteristics, process implementation, and other quality related information to identify items, services, and processes needing improvement.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            },
            {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "bd033bfa-a5a8-4134-b9b4-2f11beb4f7a2"
        },
        {
            "id": "57e0bcfe-de30-42a4-8ef3-2537077b176f",
            "clause": "Prepare, review, approve, issue, use, and revise documents to prescribe processes, specify requirements, or establish design.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "bd033bfa-a5a8-4134-b9b4-2f11beb4f7a2"
        },
        {
            "id": "09888991-739a-456a-a07e-27f6984490ca",
            "clause": "Specify, prepare, review, approve, and maintain records.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "bd033bfa-a5a8-4134-b9b4-2f11beb4f7a2"
        },
        {
            "id": "75d3f237-ce4a-4c8e-b162-0b7c924c07ba",
            "clause": "Perform work consistent with technical standards, administrative controls, and other hazard controls adopted to meet regulatory or contract requirements using approved instructions, procedures, or other appropriate means.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "bd033bfa-a5a8-4134-b9b4-2f11beb4f7a2"
        },
        {
            "id": "ed9cbdf6-8ed8-4441-bdec-b167d8270326",
            "clause": "Identify and control items to ensure proper use.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "bd033bfa-a5a8-4134-b9b4-2f11beb4f7a2"
        },
        {
            "id": "34353319-6f80-4f3e-899c-b98ada3ceb17",
            "clause": "Maintain items to prevent damage, loss, or deterioration.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "19",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "bd033bfa-a5a8-4134-b9b4-2f11beb4f7a2"
        },
        {
            "id": "f4449b7d-15b6-41d2-892f-2fc5339932ea",
            "clause": "Calibrate and maintain equipment used for process monitoring or data collection.",
            "type_of_clause": "Consultant_Clause",
            "references":[ {
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "26242a0f-318b-42b3-9ad5-30b20b8b135b",
            "clause": "Design items and processes using sound engineering/scientific principles and appropriate standards.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "e3a8e7be-d2c6-41e2-a3e0-0d58be7312df",
            "clause": "Incorporate applicable requirements and design bases in design work and design changes.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "b6d9909b-df8f-4a03-a8d0-c4502a1b43a3",
            "clause": "Identify and control design interfaces.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "23e7c9a6-2eb9-4ffb-8c67-d8ff23b02641",
            "clause": "Verify or validate the adequacy of design products using individuals or groups other than those who performed the work.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "79530124-4fe1-4c7a-b0d2-91552da34a21",
            "clause": "Verify or validate work before approval and implementation of the design.",
            "type_of_clause": "Consultant_Clause",
            "references": [{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            },{
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "3bf46caf-968d-4f12-a4b3-cbf0d84c4413",
            "clause": "Procure items and services that meet established requirements and perform as specified.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "3dce5565-68ce-436f-a035-56fc30cfb3cb",
            "clause": "Evaluate and select prospective suppliers on the basis of specified criteria.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "e5c0a755-48b3-42ce-a143-34e99db14cc7"
        },
        {
            "id": "63c6bb93-a98d-455c-a016-d9ef767703c6",
            "clause": "Inspect and test specified items, services, and processes using established acceptance and performance criteria.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3, 2",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "c44ba3f6-1817-458f-813b-fa23c3ceaf0b"
        },
        {
            "id": "e4c3838c-307c-4613-a261-c017f5f39445",
            "clause": "Calibrate and maintain equipment used for inspections and tests.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "c44ba3f6-1817-458f-813b-fa23c3ceaf0b"
        },
        {
            "id": "6920d507-f9a2-4c91-bfb2-833720b1a7f9",
            "clause": "Ensure that managers assess their management processes and identify and correct problems that hinder the organization from achieving its objectives.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "c44ba3f6-1817-458f-813b-fa23c3ceaf0b"
        },
        {
            "id": "e36c6c46-44db-4c1b-939d-2fec9beebfd9",
            "clause": "Establish sufficient authority and freedom from line management for independent assessment teams.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3",
                "File Name": "10 CFR Part 830 Subpart A."
            }
            ],
            "chunk_id": "c44ba3f6-1817-458f-813b-fa23c3ceaf0b"
        },
        {
            "id": "9a74a9e7-d603-45ba-8b0e-59d685ba8e71",
            "clause": "Ensure persons who perform independent assessments are technically qualified and knowledgeable in the areas to be assessed.",
            "type_of_clause": "Consultant_Clause",
            "references":[{
                "Page No": "20",
                "File Name": "DOE_O_414_1D"
            }, {
                "Page No": "3",
                "File Name": "10 CFR Part 830 Subpart A."
            }],
            "chunk_id": "293ecc66-80dd-4089-b0c7-26216efc4c98"
        }
    ]