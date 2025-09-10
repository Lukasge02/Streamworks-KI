/**
 * XML Generator Utility
 * Generates Streamworks-compliant XML from wizard form data
 */

import { WizardFormData, JobType, OSType, ScheduleMode } from '../types/wizard.types'

export interface GeneratedXMLResult {
  success: boolean
  xmlContent?: string
  error?: string
}

/**
 * Main function to generate XML from wizard form data
 */
export const generateStreamworksXML = (formData: Partial<WizardFormData>): GeneratedXMLResult => {
  try {
    if (!formData.jobType || !formData.streamProperties) {
      return {
        success: false,
        error: 'Missing required form data: jobType and streamProperties are required'
      }
    }

    const xml = buildCompleteXML(formData as WizardFormData)
    
    return {
      success: true,
      xmlContent: xml
    }
  } catch (error) {
    return {
      success: false,
      error: `XML generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    }
  }
}

/**
 * Build complete ExportableStream XML structure
 */
const buildCompleteXML = (formData: WizardFormData): string => {
  const streamName = formData.streamProperties.streamName
  const description = formData.streamProperties.description
  const documentation = formData.streamProperties.documentation || ''
  
  return `<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>${escapeXml(streamName)}</StreamName>
    <StreamDocumentation><![CDATA[${documentation}]]></StreamDocumentation>
    <AgentDetail>gtasswvk05445</AgentDetail>
    <AccountNoId />
    <CalendarId />
    <StreamType>Normal</StreamType>
    <MaxStreamRuns>${formData.streamProperties.maxRuns || 5}</MaxStreamRuns>
    <ShortDescription><![CDATA[${description}]]></ShortDescription>
    <SchedulingRequiredFlag>${formData.scheduling?.mode !== 'simple' || formData.scheduling?.simple?.preset !== 'manual'}</SchedulingRequiredFlag>
    <ScheduleRuleObject />
    <RuntimeDataStorageDays IsNull="True" />
    <RuntimeDataStorageDaySource IsNull="True" />
    <StreamRunDeletionSource IsNull="True" />
    <StreamRunDeletionType>None</StreamRunDeletionType>
    <StreamRunDeletionTime IsNull="True" />
    <StreamRunDeletionDays IsNull="True" />
    <StreamRunDeletionDayType IsNull="True" />
    <DeletionTimeTimeZoneId />
    <DeletionTimeValidFlag IsNull="True" />
    <DeletionTimeValidSource IsNull="True" />
    <StreamRunTimeStatisticsDays IsNull="True" />
    <AvgRunTimeCalcInDays>0</AvgRunTimeCalcInDays>
    <SeverityGroup>${escapeXml(formData.streamProperties.severityGroup || '')}</SeverityGroup>
    <MaxStreamRunDuration IsNull="True" />
    <MinStreamRunDuration IsNull="True" />
    <CentralJobLogAreaFlag IsNull="True" />
    <CentralJobLogSource IsNull="True" />
    <CentralJobLogStorageDays IsNull="True" />
    <AgentJobLogStorageDays IsNull="True" />
    <AgentJobLogStorageDaySource IsNull="True" />
    <StreamRunInterval IsNull="True" />
    <MaxJobLogSize IsNull="True" />
    <ReorgType IsNull="True" />
    <ExternalJobScriptRequired IsNull="True" />
    <KeepPreparedRuns IsNull="True" />
    <InteractivePslFlag>False</InteractivePslFlag>
    <ConcurrentPlanDatesEnabled />
    <UncatExclusion IsNull="True" />
    ${generateJobsSection(formData)}
    ${generateContactPersonsSection(formData.streamProperties.contactPerson)}
    ${generateScheduleRuleSection(formData)}
    <StreamPreparationScript>
      <Script><![CDATA[]]></Script>
      <ScriptLanguage>Lua</ScriptLanguage>
    </StreamPreparationScript>
    <MasterStreamId />
    <StreamPath><![CDATA[${escapeXml(generateStreamPath(formData))}]]></StreamPath>
    <StatusFlag>True</StatusFlag>
    <StreamVersionDetail>
      <StreamVersionType>Current</StreamVersionType>
      <StreamVersion>1.0</StreamVersion>
      <DeploymentDateTime>${new Date().toLocaleString('de-DE')}</DeploymentDateTime>
      <DeployAsActive>True</DeployAsActive>
      <PlannedDeploymentDateTime />
      <StorageDateTime />
      <AutoDeploymentStatus>Finished</AutoDeploymentStatus>
      <ScheduleRulesMergeType>FromNew</ScheduleRulesMergeType>
    </StreamVersionDetail>
    <AutomaticPreparedRuns>0</AutomaticPreparedRuns>
    <BusinessServiceFlag>False</BusinessServiceFlag>
    <StreamBusinessServiceProperty />
    <AutoPreparationType>Complete</AutoPreparationType>
    <RunVariables />
    <ConcurrentStreamRunsEnabled />
    <EnableStreamRunCancelation>False</EnableStreamRunCancelation>
    <Tags />
    <GitEnabled IsNull="True" />
  </Stream>
</ExportableStream>`
}

/**
 * Generate Jobs section based on job type and configuration
 */
const generateJobsSection = (formData: WizardFormData): string => {
  const jobs = []
  
  // Always add Recovery Start and End Points
  jobs.push(generateRecoveryStartPoint())
  jobs.push(generateRecoveryEndPoint())
  
  // Add StartPoint
  jobs.push(generateStartPoint(formData))
  
  // Add main job based on type
  if (formData.jobForm) {
    jobs.push(generateMainJob(formData))
  }
  
  // Add EndPoint
  jobs.push(generateEndPoint())
  
  return `<Jobs>
${jobs.join('\n')}
    </Jobs>`
}

/**
 * Generate Recovery Start Point Job
 */
const generateRecoveryStartPoint = (): string => {
  return `      <Job>
        <JobName>RecoveryJobNetStartPoint</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[Recovery Jobnet Start Point]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>RecoveryJobNetStartPoint</JobCategory>
        <NormalJobFlag>False</NormalJobFlag>
        <JobType>None</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>0</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>200</CoordinateX>
        <CoordinateY>100</CoordinateY>
        <JobInternalSuccessors />
        ${generateStreamRunJobProperties()}
        ${generateDefaultJobSections()}
      </Job>`
}

/**
 * Generate Recovery End Point Job
 */
const generateRecoveryEndPoint = (): string => {
  return `      <Job>
        <JobName>RecoveryJobNetEndPoint</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[Recovery Jobnet End Point]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>RecoveryJobNetEndPoint</JobCategory>
        <NormalJobFlag>False</NormalJobFlag>
        <JobType>None</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>0</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>200</CoordinateX>
        <CoordinateY>350</CoordinateY>
        <JobInternalSuccessors />
        ${generateStreamRunJobProperties()}
        ${generateDefaultJobSections()}
      </Job>`
}

/**
 * Generate Start Point Job
 */
const generateStartPoint = (formData: WizardFormData): string => {
  const mainJobName = getMainJobName(formData)
  
  return `      <Job>
        <JobName>StartPoint</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[Start Point for the Stream]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>StartPoint</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>None</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>1</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>145</CoordinateX>
        <CoordinateY>0</CoordinateY>
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>${escapeXml(mainJobName)}</JobName>
            <EdgeBreaks IsNull="True" />
            <EdgeEndPosition>2</EdgeEndPosition>
            <EdgeStartPosition>6</EdgeStartPosition>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
        ${generateStreamRunJobProperties()}
        ${generateDefaultJobSections()}
      </Job>`
}

/**
 * Generate main job based on job type
 */
const generateMainJob = (formData: WizardFormData): string => {
  switch (formData.jobType) {
    case JobType.STANDARD:
      return generateStandardJob(formData.jobForm as any)
    case JobType.SAP:
      return generateSAPJob(formData.jobForm as any)
    case JobType.FILE_TRANSFER:
      return generateFileTransferJob(formData.jobForm as any)
    default:
      return generateStandardJob(formData.jobForm as any)
  }
}

/**
 * Generate Standard Windows/Unix Job
 */
const generateStandardJob = (jobForm: any): string => {
  const jobName = jobForm.jobName || 'MainJob'
  const script = jobForm.script || 'echo "Hello World"'
  const os = jobForm.os || OSType.WINDOWS
  const jobType = os === OSType.WINDOWS ? 'Windows' : 'Unix'
  
  return `      <Job>
        <JobName>${escapeXml(jobName)}</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[${jobForm.shortDescription || jobName}]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Job</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>${jobType}</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript><![CDATA[${script}]]></MainScript>
        <DisplayOrder>2</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>145</CoordinateX>
        <CoordinateY>192</CoordinateY>
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>EndPoint</JobName>
            <EdgeBreaks IsNull="True" />
            <EdgeEndPosition>2</EdgeEndPosition>
            <EdgeStartPosition>6</EdgeStartPosition>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
        ${generateStreamRunJobProperties()}
        ${generateDefaultJobSections()}
        <JobPreparationScript>
          <PreparationScriptJobOrder>0</PreparationScriptJobOrder>
          <Script><![CDATA[]]></Script>
          <ScriptLanguage>Lua</ScriptLanguage>
        </JobPreparationScript>
      </Job>`
}

/**
 * Generate SAP Job
 */
const generateSAPJob = (jobForm: any): string => {
  const jobName = jobForm.jobName || 'SAPJob'
  
  return `      <Job>
        <JobName>${escapeXml(jobName)}</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[SAP Job: ${jobForm.report || 'Unknown'}]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Job</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>SAP</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>2</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>145</CoordinateX>
        <CoordinateY>192</CoordinateY>
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>EndPoint</JobName>
            <EdgeBreaks IsNull="True" />
            <EdgeEndPosition>2</EdgeEndPosition>
            <EdgeStartPosition>6</EdgeStartPosition>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
        ${generateStreamRunJobProperties()}
        ${generateSAPJobProperty(jobForm)}
        ${generateDefaultJobSections()}
      </Job>`
}

/**
 * Generate File Transfer Job
 */
const generateFileTransferJob = (jobForm: any): string => {
  const jobName = jobForm.jobName || 'FileTransferJob'
  
  return `      <Job>
        <JobName>${escapeXml(jobName)}</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[File Transfer]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Job</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>None</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>2</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>FileTransfer</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>145</CoordinateX>
        <CoordinateY>208</CoordinateY>
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>EndPoint</JobName>
            <EdgeBreaks IsNull="True" />
            <EdgeEndPosition>2</EdgeEndPosition>
            <EdgeStartPosition>6</EdgeStartPosition>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
        ${generateStreamRunJobProperties()}
        ${generateFileTransferProperty(jobForm)}
        ${generateDefaultJobSections()}
      </Job>`
}

/**
 * Generate End Point Job
 */
const generateEndPoint = (): string => {
  return `      <Job>
        <JobName>EndPoint</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[End Point for the Stream]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Endpoint</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>None</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>3</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>135</CoordinateX>
        <CoordinateY>416</CoordinateY>
        <JobInternalSuccessors />
        ${generateStreamRunJobProperties()}
        ${generateDefaultJobSections()}
      </Job>`
}

/**
 * Generate SAP Job Property section
 */
const generateSAPJobProperty = (jobForm: any): string => {
  return `        <JobSAPProperty>
          <SystemName>${escapeXml(jobForm.system || '')}</SystemName>
          <ReportName>${escapeXml(jobForm.report || '')}</ReportName>
          <VariantName>${escapeXml(jobForm.variant || '')}</VariantName>
          <BatchUserName>${escapeXml(jobForm.batchUser || '')}</BatchUserName>
          <SelectionParameters>
${(jobForm.selectionParameters || []).map((param: any, index: number) => 
    `            <SelectionParameter>
              <PositionNo>${index + 1}</PositionNo>
              <Parameter>${escapeXml(param.parameter)}</Parameter>
              <Sign>${escapeXml(param.sign || 'I')}</Sign>
              <Option>${escapeXml(param.option || 'EQ')}</Option>
              <Low>${escapeXml(param.low || param.value || '')}</Low>
              <High>${escapeXml(param.high || '')}</High>
            </SelectionParameter>`
  ).join('\n')}
          </SelectionParameters>
        </JobSAPProperty>`
}

/**
 * Generate File Transfer Property section
 */
const generateFileTransferProperty = (jobForm: any): string => {
  return `        <JobFileTransferProperty>
          <SourceAgent>${escapeXml(jobForm.sourceAgent || '')}</SourceAgent>
          <TargetAgent>${escapeXml(jobForm.targetAgent || '')}</TargetAgent>
          <SourceLoginObject />
          <TargetLoginObject />
          <FileTransferDefinitions>
            <FileTransferDefinition>
              <PositionNo>1</PositionNo>
              <SourceFilePattern><![CDATA[${jobForm.sourcePath || ''}]]></SourceFilePattern>
              <ControlFilePathFlag>False</ControlFilePathFlag>
              <TargetFilePath><![CDATA[${jobForm.targetPath || ''}]]></TargetFilePath>
              <TargetFileName><![CDATA[${jobForm.fileName || ''}]]></TargetFileName>
              <SourceUnfulfilledHandling>Abort</SourceUnfulfilledHandling>
              <SourceFileDeleteFlag>${jobForm.deleteAfterTransfer || false}</SourceFileDeleteFlag>
              <TargetFileExistsHandling>${escapeXml(jobForm.onExistsBehavior || 'Overwrite')}</TargetFileExistsHandling>
              <SourceEncodingDetail />
              <TargetEncodingDetail />
              <DeleteTrailingBlanksFlag>False</DeleteTrailingBlanksFlag>
              <LinebreakTranslationType>None</LinebreakTranslationType>
              <UseSourceAttributesFlag>False</UseSourceAttributesFlag>
            </FileTransferDefinition>
          </FileTransferDefinitions>
        </JobFileTransferProperty>`
}

/**
 * Generate StreamRunJobProperties (common to all jobs)
 */
const generateStreamRunJobProperties = (): string => {
  return `        <StreamRunJobProperties>
          <StreamRunJobProperty>
            <RunNumber>0</RunNumber>
            <StartTime IsNull="True" />
            <StartTimeDayType />
            <StartTimeOffsetDays IsNull="True" />
            <StartTimeTimeZone />
            <StartTimeType IsNull="True" />
            <RelativeStartTime IsNull="True" />
            <StartTimeRelativeJob />
            <MaxJobLogSize IsNull="True" />
            <MaxJobDuration IsNull="True" />
            <LatestStartTime IsNull="True" />
            <LatestStartTimeType IsNull="True" />
            <LatestStartTimeRelative IsNull="True" />
            <LatestStartTimeOffsetDays IsNull="True" />
            <LatestStartTimeDayType IsNull="True" />
            <LatestStartTimeConsiderAfterRestart IsNull="True" />
            <LatestStartTimeAction IsNull="True" />
            <JobHoldFlag IsNull="True" />
            <CentralJobLogFlag IsNull="True" />
            <BypassStatus IsNull="True" />
            <AgentDetail />
            <AgentSource IsNull="True" />
            <AccountDetail />
            <AccountSource IsNull="True" />
            <SeverityGroup />
            <AgentJobLogStorageDays IsNull="True" />
            <ExternalDependencies />
            <FileDependency />
            <JobCompletionCodeRules />
            <LogicalResourceDependencies />
            <Documentation IsNull="True" />
          </StreamRunJobProperty>
          <StreamRunJobProperty>
            <RunNumber>1</RunNumber>
            <StartTime IsNull="True" />
            <StartTimeDayType />
            <StartTimeOffsetDays IsNull="True" />
            <StartTimeTimeZone />
            <StartTimeType IsNull="True" />
            <RelativeStartTime IsNull="True" />
            <StartTimeRelativeJob />
            <MaxJobLogSize IsNull="True" />
            <MaxJobDuration IsNull="True" />
            <LatestStartTime IsNull="True" />
            <LatestStartTimeType IsNull="True" />
            <LatestStartTimeRelative IsNull="True" />
            <LatestStartTimeOffsetDays IsNull="True" />
            <LatestStartTimeDayType IsNull="True" />
            <LatestStartTimeConsiderAfterRestart IsNull="True" />
            <LatestStartTimeAction IsNull="True" />
            <JobHoldFlag IsNull="True" />
            <CentralJobLogFlag IsNull="True" />
            <BypassStatus IsNull="True" />
            <AgentDetail />
            <AgentSource IsNull="True" />
            <AccountDetail />
            <AccountSource IsNull="True" />
            <SeverityGroup />
            <AgentJobLogStorageDays IsNull="True" />
            <ExternalDependencies />
            <FileDependency />
            <JobCompletionCodeRules />
            <LogicalResourceDependencies />
            <Documentation IsNull="True" />
          </StreamRunJobProperty>
        </StreamRunJobProperties>`
}

/**
 * Generate default job sections (common to all jobs)
 */
const generateDefaultJobSections = (): string => {
  return `        <JobContactPersons />
        <JobPreparationScript />
        <RecoveryRules />
        <ParserJobDefinitions />
        <JobExtensions />
        <ControlFilePathLoginObject />
        <ExternalProcedureDependencies />`
}

/**
 * Generate contact persons section
 */
const generateContactPersonsSection = (contactPerson: any): string => {
  return `    <StreamContactPersons>
      <StreamContactPerson>
        <FirstName>${escapeXml(contactPerson.firstName || '')}</FirstName>
        <LastName>${escapeXml(contactPerson.lastName || '')}</LastName>
        <MiddleName />
        <CompanyName>${escapeXml(contactPerson.company || 'Arvato Systems')}</CompanyName>
        <Department>${escapeXml(contactPerson.department || '')}</Department>
        <Comment IsNull="True" />
        <ContactType>None</ContactType>
        <HierarchyLevelCd>1</HierarchyLevelCd>
      </StreamContactPerson>
    </StreamContactPersons>`
}

/**
 * Generate schedule rule section
 */
const generateScheduleRuleSection = (formData: WizardFormData): string => {
  const scheduling = formData.scheduling
  
  if (!scheduling || scheduling.mode === ScheduleMode.SIMPLE && scheduling.simple?.preset === 'manual') {
    return `    <ScheduleRule>
      <ScheduleRuleXml><![CDATA[&lt;SchedulingRules ShiftRule=&quot;3&quot; ScheduleRuleDialogNotYetVisited=&quot;1&quot; /&gt;]]></ScheduleRuleXml>
    </ScheduleRule>`
  }
  
  // For non-manual scheduling, generate more complex rules
  let scheduleRuleXml = '&lt;SchedulingRules ShiftRule=&quot;3&quot; ScheduleRuleDialogNotYetVisited=&quot;0&quot;&gt;'
  
  if (scheduling.mode === ScheduleMode.SIMPLE && scheduling.simple) {
    const simple = scheduling.simple
    if (simple.preset === 'daily' && simple.time) {
      scheduleRuleXml += `&lt;FixedDates&gt;&lt;FixedDate Time=&quot;${simple.time}&quot; DayType=&quot;Daily&quot; /&gt;&lt;/FixedDates&gt;`
    } else if (simple.preset === 'weekly' && simple.weekdays && simple.time) {
      const weekdayString = simple.weekdays.map((day, idx) => day ? (idx + 1).toString() : '').filter(Boolean).join(',')
      scheduleRuleXml += `&lt;FixedDates&gt;&lt;FixedDate Time=&quot;${simple.time}&quot; DayType=&quot;Weekly&quot; Weekdays=&quot;${weekdayString}&quot; /&gt;&lt;/FixedDates&gt;`
    }
  }
  
  scheduleRuleXml += '&lt;/SchedulingRules&gt;'
  
  return `    <ScheduleRule>
      <ScheduleRuleXml><![CDATA[${scheduleRuleXml}]]></ScheduleRuleXml>
    </ScheduleRule>`
}

/**
 * Utility functions
 */
const escapeXml = (text: string): string => {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

/**
 * Generate appropriate stream path based on job type and stream properties
 */
const generateStreamPath = (formData: WizardFormData): string => {
  // Use custom path if provided
  if (formData.streamProperties?.streamPath && formData.streamProperties.streamPath !== '/') {
    return formData.streamProperties.streamPath
  }
  
  // Generate path based on job type
  switch (formData.jobType) {
    case JobType.FILE_TRANSFER:
      return '/FT'
    case JobType.SAP:
      return '/SAP'
    case JobType.STANDARD:
      return '/STANDARD'
    default:
      return '/'
  }
}

const getMainJobName = (formData: WizardFormData): string => {
  if (formData.jobForm && 'jobName' in formData.jobForm) {
    return formData.jobForm.jobName as string
  }
  return 'MainJob'
}

/**
 * Simple XML validation
 */
export const validateXML = (xmlContent: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  
  // Basic XML structure validation
  if (!xmlContent.includes('<?xml')) {
    errors.push('Missing XML declaration')
  }
  
  if (!xmlContent.includes('<ExportableStream>')) {
    errors.push('Missing ExportableStream root element')
  }
  
  if (!xmlContent.includes('</ExportableStream>')) {
    errors.push('Missing closing ExportableStream tag')
  }
  
  // Check for balanced tags (simple check)
  const openTags = (xmlContent.match(/<[^\/!][^>]*>/g) || []).length
  const closeTags = (xmlContent.match(/<\/[^>]*>/g) || []).length
  const selfClosingTags = (xmlContent.match(/<[^>]*\/>/g) || []).length
  
  if (openTags !== closeTags + selfClosingTags) {
    errors.push('Unbalanced XML tags detected')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}