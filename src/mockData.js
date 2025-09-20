// New mock data for Healthcare AI Test Case Generator based on SRS

// Compliance standards used in the SRS
export const complianceStandards = [
  { id: 'HIPAA', name: 'HIPAA Equivalent', color: '#8E24AA' },
  { id: 'AES-256', name: 'AES-256', color: '#1A237E' },
  { id: 'TLS1.2+', name: 'TLS 1.2+', color: '#00695C' }
];

// Mock requirements data from the SRS
export const requirements = [
  {
    id: 'REQ-001',
    description: 'The system shall allow new patients to register using name, date of birth, gender, email, phone number, and address.',
    complianceRefs: ['HIPAA']
  },
  {
    id: 'REQ-002',
    description: 'The system shall support secure login for patients and staff using email/phone and password, with MFA for doctors and administrators.',
    complianceRefs: ['HIPAA', 'TLS1.2+']
  },
  {
    id: 'REQ-003',
    description: 'Patients shall be able to book, cancel, and reschedule appointments online, and doctors can set availability.',
    complianceRefs: []
  },
  {
    id: 'REQ-004',
    description: 'Doctors shall be able to upload consultation notes, lab results, and prescriptions to a patient\'s EMR, and patients can view but not edit their EMR.',
    complianceRefs: ['HIPAA', 'AES-256']
  },
  {
    id: 'REQ-005',
    description: 'The system shall auto-generate invoices after consultations and support multiple payment methods.',
    complianceRefs: []
  },
  {
    id: 'REQ-006',
    description: 'Patients shall receive SMS/email reminders 24 hours before appointments.',
    complianceRefs: []
  },
  {
    id: 'REQ-007',
    description: 'The system shall log all access to patient records with timestamp, user ID, and action performed.',
    complianceRefs: ['HIPAA']
  },
  {
    id: 'REQ-008',
    description: 'The system shall support at least 500 concurrent users with <2 seconds response time.',
    complianceRefs: []
  }
];

// Mock test case data from the SRS
export const testCases = [
  {
    id: 'TC-001',
    title: 'Verify patient registration with valid data',
    requirementId: 'REQ-001',
    steps: '1. Navigate to patient registration.\n2. Enter all valid details.\n3. Submit form.',
    expectedResult: 'Patient account is created successfully.',
    priority: 'High',
    complianceRefs: ['HIPAA'],
    status: 'Not Tested'
  },
  {
    id: 'TC-002',
    title: 'Verify phone number and email format validation',
    requirementId: 'REQ-001',
    steps: '1. Enter invalid phone and email formats.\n2. Attempt to submit.',
    expectedResult: 'System displays format errors and prevents submission.',
    priority: 'High',
    complianceRefs: ['HIPAA'],
    status: 'Pass'
  },
  {
    id: 'TC-003',
    title: 'Verify MFA for doctor login',
    requirementId: 'REQ-002',
    steps: '1. Login as a doctor.\n2. Enter credentials.\n3. Verify MFA prompt.',
    expectedResult: 'Doctor is prompted for and successfully authenticates with MFA.',
    priority: 'High',
    complianceRefs: ['HIPAA', 'TLS1.2+'],
    status: 'Pass'
  },
  {
    id: 'TC-004',
    title: 'Verify double-booking is prevented',
    requirementId: 'REQ-003',
    steps: '1. Log in as Patient A and book a slot.\n2. Log in as Patient B.\n3. Attempt to book the same slot.',
    expectedResult: 'Patient B is prevented from booking the same time slot.',
    priority: 'High',
    complianceRefs: [],
    status: 'Fail'
  },
  {
    id: 'TC-005',
    title: 'Verify EMR encryption at rest',
    requirementId: 'REQ-004',
    steps: '1. Upload notes to EMR.\n2. Access database directly.\n3. Verify data is encrypted.',
    expectedResult: 'EMR data is stored in an encrypted format.',
    priority: 'Critical',
    complianceRefs: ['HIPAA', 'AES-256'],
    status: 'Not Tested'
  },
  {
    id: 'TC-006',
    title: 'Verify patient cannot edit EMR',
    requirementId: 'REQ-004',
    steps: '1. Log in as a patient.\n2. Attempt to edit EMR notes.',
    expectedResult: 'Patient is unable to edit or save changes to the EMR.',
    priority: 'High',
    complianceRefs: ['HIPAA'],
    status: 'Pass'
  },
  {
    id: 'TC-007',
    title: 'Verify audit log for patient record access',
    requirementId: 'REQ-007',
    steps: '1. Access a patient record.\n2. Check the audit trail.',
    expectedResult: 'Audit log contains a record of the access with user ID, timestamp, and action.',
    priority: 'High',
    complianceRefs: ['HIPAA'],
    status: 'Pass'
  }
];

// Mock audit trail data based on SRS
export const auditTrail = [
  {
    id: 'AT-001',
    user: 'doctor@example.com',
    action: 'Generated test cases',
    filename: 'SRS.pdf',
    timestamp: '2025-09-20T10:00:00Z'
  },
  {
    id: 'AT-002',
    user: 'patient@example.com',
    action: 'Accessed patient record',
    filename: 'Patient_JaneDoe.EMR',
    timestamp: '2025-09-20T10:05:00Z'
  },
  {
    id: 'AT-003',
    user: 'admin@example.com',
    action: 'Exported RTM',
    filename: 'RTM_Export_20250920.csv',
    timestamp: '2025-09-20T10:10:00Z'
  }
];

// Dashboard statistics
export const dashboardStats = {
  totalRequirements: 8,
  totalTestCases: 7,
  traceabilityCoverage: 87, 
  edgeCasesIdentified: 3
};

// Mock clarifying questions
export const clarifyingQuestions = [
  {
    id: 'Q1',
    question: 'Are there specific security requirements for API endpoints?',
    options: ['Yes', 'No']
  },
  {
    id: 'Q2',
    question: 'Which compliance standards are most critical?',
    options: ['HIPAA', 'FDA 21 CFR Part 11', 'ISO 13485', 'IEC 62304']
  },
  {
    id: 'Q3',
    question: 'Should the test cases include performance tests for concurrent users?',
    options: ['Yes', 'No']
  }
];