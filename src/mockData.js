// Mock data for Healthcare AI Test Case Generator

// Compliance standards used in healthcare software testing
export const complianceStandards = [
  { id: 'FDA21CFR11', name: 'FDA 21 CFR Part 11', color: '#FF5722' },
  { id: 'ISO13485', name: 'ISO 13485', color: '#2196F3' },
  { id: 'IEC62304', name: 'IEC 62304', color: '#4CAF50' },
  { id: 'ISO27001', name: 'ISO 27001', color: '#9C27B0' }
];

// Mock requirements data
export const requirements = [
  {
    id: 'REQ-001',
    description: 'The system shall authenticate users with multi-factor authentication',
    complianceRefs: ['ISO27001', 'FDA21CFR11']
  },
  {
    id: 'REQ-002',
    description: 'The system shall encrypt all patient data at rest and in transit',
    complianceRefs: ['ISO27001', 'FDA21CFR11']
  },
  {
    id: 'REQ-003',
    description: 'The system shall maintain an audit trail of all data modifications',
    complianceRefs: ['FDA21CFR11', 'ISO13485']
  },
  {
    id: 'REQ-004',
    description: 'The system shall validate all input data for type, range, and format',
    complianceRefs: ['IEC62304']
  },
  {
    id: 'REQ-005',
    description: 'The system shall provide role-based access control',
    complianceRefs: ['ISO27001', 'FDA21CFR11']
  },
  {
    id: 'REQ-006',
    description: 'The system shall generate alerts for critical patient values',
    complianceRefs: ['IEC62304', 'ISO13485']
  },
  {
    id: 'REQ-007',
    description: 'The system shall maintain data integrity through checksums',
    complianceRefs: ['FDA21CFR11']
  },
  {
    id: 'REQ-008',
    description: 'The system shall provide a mechanism for electronic signatures',
    complianceRefs: ['FDA21CFR11']
  }
];

// Mock test case data
export const testCases = [
  {
    id: 'TC-001',
    title: 'Verify MFA Authentication',
    requirementId: 'REQ-001',
    steps: '1. Navigate to login page\n2. Enter valid credentials\n3. Verify MFA prompt appears\n4. Enter valid MFA code',
    expectedResult: 'User is authenticated and directed to the dashboard',
    priority: 'High',
    complianceRefs: ['ISO27001', 'FDA21CFR11'],
    status: 'Pass'
  },
  {
    id: 'TC-002',
    title: 'Verify Data Encryption at Rest',
    requirementId: 'REQ-002',
    steps: '1. Store patient data in the database\n2. Access database directly\n3. Verify stored data is encrypted',
    expectedResult: 'Data in database appears encrypted and unreadable',
    priority: 'High',
    complianceRefs: ['ISO27001', 'FDA21CFR11'],
    status: 'Pass'
  },
  {
    id: 'TC-003',
    title: 'Verify Audit Trail Creation',
    requirementId: 'REQ-003',
    steps: '1. Login as admin\n2. Modify patient record\n3. Access audit log\n4. Verify modification is recorded',
    expectedResult: 'Audit log shows user ID, timestamp, and modified data',
    priority: 'Medium',
    complianceRefs: ['FDA21CFR11', 'ISO13485'],
    status: 'Fail'
  },
  {
    id: 'TC-004',
    title: 'Verify Input Validation - Invalid Data',
    requirementId: 'REQ-004',
    steps: '1. Navigate to patient data entry\n2. Enter invalid data (e.g., letters in age field)\n3. Attempt to save',
    expectedResult: 'System displays validation error and prevents saving',
    priority: 'Medium',
    complianceRefs: ['IEC62304'],
    status: 'Pass'
  },
  {
    id: 'TC-005',
    title: 'Verify Role-Based Access - Restricted Area',
    requirementId: 'REQ-005',
    steps: '1. Login as basic user\n2. Attempt to access admin settings',
    expectedResult: 'Access denied message displayed',
    priority: 'High',
    complianceRefs: ['ISO27001', 'FDA21CFR11'],
    status: 'Not Tested'
  },
  {
    id: 'TC-006',
    title: 'Verify Critical Value Alerts',
    requirementId: 'REQ-006',
    steps: '1. Enter critical blood pressure value\n2. Save patient record',
    expectedResult: 'Visual alert appears and notification is sent',
    priority: 'High',
    complianceRefs: ['IEC62304', 'ISO13485'],
    status: 'Pass'
  },
  {
    id: 'TC-007',
    title: 'Verify Data Integrity with Invalid Checksum',
    requirementId: 'REQ-007',
    steps: '1. Modify data directly in database to break checksum\n2. Attempt to access record via application',
    expectedResult: 'System detects tampering and displays integrity error',
    priority: 'Medium',
    complianceRefs: ['FDA21CFR11'],
    status: 'Not Tested'
  },
  {
    id: 'TC-008',
    title: 'Verify Electronic Signature Capture',
    requirementId: 'REQ-008',
    steps: '1. Complete medical form\n2. Prompt for electronic signature\n3. Enter credentials for signing',
    expectedResult: 'Document is signed with user ID, timestamp, and reason for signing',
    priority: 'Medium',
    complianceRefs: ['FDA21CFR11'],
    status: 'Fail'
  }
];

// Mock audit trail data
export const auditTrail = [
  {
    id: 'AT-001',
    user: 'john.doe@healthcare.org',
    action: 'File Upload',
    filename: 'PatientCare_Requirements_v1.2.pdf',
    timestamp: '2023-07-15T09:23:45Z'
  },
  {
    id: 'AT-002',
    user: 'john.doe@healthcare.org',
    action: 'Test Case Generation',
    filename: 'PatientCare_Requirements_v1.2.pdf',
    timestamp: '2023-07-15T09:25:12Z'
  },
  {
    id: 'AT-003',
    user: 'jane.smith@healthcare.org',
    action: 'File Upload',
    filename: 'MedicationModule_Requirements.docx',
    timestamp: '2023-07-16T14:05:33Z'
  },
  {
    id: 'AT-004',
    user: 'jane.smith@healthcare.org',
    action: 'Test Case Generation',
    filename: 'MedicationModule_Requirements.docx',
    timestamp: '2023-07-16T14:08:21Z'
  },
  {
    id: 'AT-005',
    user: 'jane.smith@healthcare.org',
    action: 'Test Case Regeneration',
    filename: 'MedicationModule_Requirements.docx',
    timestamp: '2023-07-16T15:45:10Z'
  },
  {
    id: 'AT-006',
    user: 'admin@healthcare.org',
    action: 'Export RTM',
    filename: 'RTM_Export_20230717.csv',
    timestamp: '2023-07-17T10:12:05Z'
  }
];

// Dashboard statistics
export const dashboardStats = {
  totalRequirements: 8,
  totalTestCases: 8,
  traceabilityCoverage: 100, // percentage
  edgeCasesIdentified: 3
};

// Mock clarifying questions for regeneration
export const clarifyingQuestions = [
  {
    id: 'Q1',
    question: 'Would you like to include negative testing scenarios?',
    options: ['Yes', 'No']
  },
  {
    id: 'Q2',
    question: 'Which compliance standards are most important for this feature?',
    options: ['FDA 21 CFR Part 11', 'ISO 13485', 'IEC 62304', 'ISO 27001']
  },
  {
    id: 'Q3',
    question: 'Should performance testing be included?',
    options: ['Yes', 'No']
  },
  {
    id: 'Q4',
    question: 'Are there specific security concerns to address?',
    options: ['Authentication', 'Authorization', 'Data Encryption', 'Input Validation', 'None']
  }
];