#!/usr/bin/env python3
"""
XSD Schema Generator for Streamworks XML Templates
Generates XSD schema based on analysis of 991 real Streamworks exports
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any
from xml.dom.minidom import parseString

class StreamworksXSDGenerator:
    def __init__(self, analysis_file: str):
        with open(analysis_file, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)

        self.element_freq = self.analysis['element_frequency']
        self.attribute_patterns = self.analysis['attribute_patterns']
        self.text_patterns = self.analysis['text_content_patterns']

    def generate_base_xsd(self) -> str:
        """Generate complete XSD schema for Streamworks exports"""

        xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           elementFormDefault="qualified">

  <!-- Root element -->
  <xs:element name="ExportableStream">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="Stream" type="StreamType"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>

  <!-- Main Stream Type -->
  <xs:complexType name="StreamType">
    <xs:sequence>
      <xs:element name="StreamName" type="xs:string"/>
      <xs:element name="StreamDocumentation">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="AgentDetail" type="xs:string" minOccurs="0"/>
      <xs:element name="AccountNoId" type="xs:string" minOccurs="0"/>
      <xs:element name="CalendarId" type="xs:string" minOccurs="0"/>
      <xs:element name="StreamType" type="StreamTypeEnum"/>
      <xs:element name="MaxStreamRuns" type="xs:int"/>
      <xs:element name="ShortDescription">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="SchedulingRequiredFlag" type="xs:boolean"/>
      <xs:element name="ScheduleRuleObject" type="xs:string" minOccurs="0"/>
      <xs:element name="OverviewInfoMessage" type="NullableString" minOccurs="0"/>
      <xs:element name="RuntimeDataStorageDays" type="NullableInt"/>
      <xs:element name="RuntimeDataStorageDaySource" type="NullableString"/>
      <xs:element name="StreamRunDeletionSource" type="NullableString"/>
      <xs:element name="StreamRunDeletionType" type="xs:string"/>
      <xs:element name="StreamRunDeletionTime" type="NullableString"/>
      <xs:element name="StreamRunDeletionDays" type="NullableInt"/>
      <xs:element name="StreamRunDeletionDayType" type="NullableString"/>
      <xs:element name="DeletionTimeTimeZoneId" type="xs:string" minOccurs="0"/>
      <xs:element name="DeletionTimeValidFlag" type="NullableBoolean"/>
      <xs:element name="DeletionTimeValidSource" type="NullableString"/>
      <xs:element name="StreamRunTimeStatisticsDays" type="NullableInt"/>
      <xs:element name="AvgRunTimeCalcInDays" type="xs:int"/>
      <xs:element name="SeverityGroup" type="xs:string" minOccurs="0"/>
      <xs:element name="SeverityId" type="xs:string" minOccurs="0"/>
      <xs:element name="MaxStreamRunDuration" type="NullableInt"/>
      <xs:element name="MinStreamRunDuration" type="NullableInt"/>
      <xs:element name="CentralJobLogAreaFlag" type="NullableBoolean"/>
      <xs:element name="CentralJobLogSource" type="xs:string" minOccurs="0"/>
      <xs:element name="CentralJobLogStorageDays" type="NullableInt"/>
      <xs:element name="AgentJobLogStorageDays" type="NullableInt"/>
      <xs:element name="AgentJobLogStorageDaySource" type="xs:string" minOccurs="0"/>
      <xs:element name="StreamRunInterval" type="NullableInt"/>
      <xs:element name="MaxJobLogSize" type="NullableInt"/>
      <xs:element name="ReorgType" type="NullableString"/>
      <xs:element name="ExternalJobScriptRequired" type="NullableBoolean"/>
      <xs:element name="KeepPreparedRuns" type="NullableInt"/>
      <xs:element name="InteractivePslFlag" type="xs:boolean"/>
      <xs:element name="ConcurrentPlanDatesEnabled" type="xs:boolean" minOccurs="0"/>
      <xs:element name="UncatExclusion" type="NullableString"/>

      <!-- Jobs section -->
      <xs:element name="Jobs" type="JobsType"/>

      <!-- Stream Contact Persons -->
      <xs:element name="StreamContactPersons" type="StreamContactPersonsType" minOccurs="0"/>

      <!-- Schedule Rule -->
      <xs:element name="ScheduleRule" type="ScheduleRuleType" minOccurs="0"/>

      <!-- Stream Preparation Script -->
      <xs:element name="StreamPreparationScript" type="PreparationScriptType" minOccurs="0"/>

      <!-- Stream Metadata -->
      <xs:element name="MasterStreamId" type="xs:string" minOccurs="0"/>
      <xs:element name="StreamPath">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="StatusFlag" type="xs:boolean"/>

      <!-- Stream Version Detail -->
      <xs:element name="StreamVersionDetail" type="StreamVersionDetailType" minOccurs="0"/>

      <!-- Additional Stream Properties -->
      <xs:element name="AutomaticPreparedRuns" type="xs:int"/>
      <xs:element name="BusinessServiceFlag" type="xs:boolean"/>
      <xs:element name="StreamBusinessServiceProperty" type="xs:string" minOccurs="0"/>
      <xs:element name="AutoPreparationType" type="xs:string"/>
      <xs:element name="RunVariables" type="xs:string" minOccurs="0"/>
      <xs:element name="ConcurrentStreamRunsEnabled" type="xs:string" minOccurs="0"/>
      <xs:element name="EnableStreamRunCancelation" type="xs:boolean"/>
      <xs:element name="Tags" type="xs:string" minOccurs="0"/>
      <xs:element name="GitEnabled" type="NullableBoolean"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Jobs Type -->
  <xs:complexType name="JobsType">
    <xs:sequence>
      <xs:element name="Job" type="JobType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Job Type -->
  <xs:complexType name="JobType">
    <xs:sequence>
      <xs:element name="JobName" type="xs:string"/>
      <xs:element name="JobDocumentation" type="NullableString"/>
      <xs:element name="JobNotificationRules" type="xs:string" minOccurs="0"/>
      <xs:element name="LoginObject" type="xs:string" minOccurs="0"/>
      <xs:element name="ShortDescription">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="StatusFlag" type="xs:boolean"/>
      <xs:element name="JobCategory" type="JobCategoryEnum"/>
      <xs:element name="NormalJobFlag" type="xs:boolean"/>
      <xs:element name="JobType" type="JobTypeEnum"/>
      <xs:element name="MinJobDuration" type="NullableInt"/>
      <xs:element name="CentralJobLogStorageDays" type="NullableInt"/>
      <xs:element name="ReportToIncidentManagementFlag" type="NullableBoolean"/>
      <xs:element name="ExternalJobScriptRequired" type="NullableBoolean"/>
      <xs:element name="MainScript" type="NullableString"/>
      <xs:element name="DisplayOrder" type="xs:int"/>
      <xs:element name="JobShortName" type="NullableString"/>
      <xs:element name="TemplateType" type="TemplateTypeEnum"/>
      <xs:element name="ControlFilePath" type="NullableString"/>
      <xs:element name="IsNotificationRequired" type="xs:boolean"/>
      <xs:element name="CoordinateX" type="xs:int"/>
      <xs:element name="CoordinateY" type="xs:int"/>

      <!-- Job Internal Successors -->
      <xs:element name="JobInternalSuccessors" type="JobInternalSuccessorsType" minOccurs="0"/>

      <!-- Stream Run Job Properties -->
      <xs:element name="StreamRunJobProperties" type="StreamRunJobPropertiesType"/>

      <!-- Job Contact Persons -->
      <xs:element name="JobContactPersons" type="xs:string" minOccurs="0"/>

      <!-- Job Preparation Script -->
      <xs:element name="JobPreparationScript" type="JobPreparationScriptType" minOccurs="0"/>

      <!-- Recovery Rules -->
      <xs:element name="RecoveryRules" type="xs:string" minOccurs="0"/>

      <!-- Parser Job Definitions -->
      <xs:element name="ParserJobDefinitions" type="xs:string" minOccurs="0"/>

      <!-- Job Extensions -->
      <xs:element name="JobExtensions" type="xs:string" minOccurs="0"/>

      <!-- Control File Path Login Object -->
      <xs:element name="ControlFilePathLoginObject" type="xs:string" minOccurs="0"/>

      <!-- External Procedure Dependencies -->
      <xs:element name="ExternalProcedureDependencies" type="xs:string" minOccurs="0"/>

      <!-- File Transfer Property (optional, for FILE_TRANSFER jobs) -->
      <xs:element name="JobFileTransferProperty" type="JobFileTransferPropertyType" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>

  <!-- File Transfer Property Type -->
  <xs:complexType name="JobFileTransferPropertyType">
    <xs:sequence>
      <xs:element name="SourceAgent" type="xs:string"/>
      <xs:element name="TargetAgent" type="xs:string"/>
      <xs:element name="SourceLoginObject" type="xs:string" minOccurs="0"/>
      <xs:element name="TargetLoginObject" type="xs:string" minOccurs="0"/>
      <xs:element name="FileTransferDefinitions" type="FileTransferDefinitionsType"/>
    </xs:sequence>
  </xs:complexType>

  <!-- File Transfer Definitions -->
  <xs:complexType name="FileTransferDefinitionsType">
    <xs:sequence>
      <xs:element name="FileTransferDefinition" type="FileTransferDefinitionType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <!-- File Transfer Definition -->
  <xs:complexType name="FileTransferDefinitionType">
    <xs:sequence>
      <xs:element name="PositionNo" type="xs:int"/>
      <xs:element name="SourceFilePattern">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="ControlFilePathFlag" type="xs:boolean"/>
      <xs:element name="TargetFilePath">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="TargetFileName">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="SourceUnfulfilledHandling" type="xs:string"/>
      <xs:element name="SourceFileDeleteFlag" type="xs:boolean"/>
      <xs:element name="TargetFileExistsHandling" type="xs:string"/>
      <xs:element name="SourceEncodingDetail" type="xs:string" minOccurs="0"/>
      <xs:element name="TargetEncodingDetail" type="xs:string" minOccurs="0"/>
      <xs:element name="DeleteTrailingBlanksFlag" type="xs:boolean"/>
      <xs:element name="LinebreakTranslationType" type="xs:string"/>
      <xs:element name="UseSourceAttributesFlag" type="xs:boolean"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Job Internal Successors -->
  <xs:complexType name="JobInternalSuccessorsType">
    <xs:sequence>
      <xs:element name="JobInternalSuccessor" type="JobInternalSuccessorType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Job Internal Successor -->
  <xs:complexType name="JobInternalSuccessorType">
    <xs:sequence>
      <xs:element name="JobName" type="xs:string"/>
      <xs:element name="EdgeBreaks" type="NullableString"/>
      <xs:element name="EdgeEndPosition" type="xs:int"/>
      <xs:element name="EdgeStartPosition" type="xs:int"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Stream Run Job Properties -->
  <xs:complexType name="StreamRunJobPropertiesType">
    <xs:sequence>
      <xs:element name="StreamRunJobProperty" type="StreamRunJobPropertyType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Stream Run Job Property -->
  <xs:complexType name="StreamRunJobPropertyType">
    <xs:sequence>
      <xs:element name="RunNumber" type="xs:int"/>
      <xs:element name="StartTime" type="NullableString"/>
      <xs:element name="StartTimeDayType" type="xs:string" minOccurs="0"/>
      <xs:element name="StartTimeOffsetDays" type="NullableInt"/>
      <xs:element name="StartTimeTimeZone" type="xs:string" minOccurs="0"/>
      <xs:element name="StartTimeType" type="NullableString"/>
      <xs:element name="RelativeStartTime" type="NullableString"/>
      <xs:element name="StartTimeRelativeJob" type="xs:string" minOccurs="0"/>
      <xs:element name="MaxJobLogSize" type="NullableInt"/>
      <xs:element name="MaxJobDuration" type="NullableInt"/>
      <xs:element name="LatestStartTime" type="NullableString"/>
      <xs:element name="LatestStartTimeType" type="NullableString"/>
      <xs:element name="LatestStartTimeRelative" type="NullableString"/>
      <xs:element name="LatestStartTimeOffsetDays" type="NullableInt"/>
      <xs:element name="LatestStartTimeDayType" type="NullableString"/>
      <xs:element name="LatestStartTimeConsiderAfterRestart" type="NullableBoolean"/>
      <xs:element name="LatestStartTimeAction" type="NullableString"/>
      <xs:element name="JobHoldFlag" type="NullableBoolean"/>
      <xs:element name="CentralJobLogFlag" type="NullableBoolean"/>
      <xs:element name="BypassStatus" type="NullableString"/>
      <xs:element name="AgentDetail" type="xs:string" minOccurs="0"/>
      <xs:element name="AgentSource" type="NullableString"/>
      <xs:element name="AccountDetail" type="xs:string" minOccurs="0"/>
      <xs:element name="AccountSource" type="NullableString"/>
      <xs:element name="SeverityGroup" type="xs:string" minOccurs="0"/>
      <xs:element name="AgentJobLogStorageDays" type="NullableInt"/>
      <xs:element name="ExternalDependencies" type="xs:string" minOccurs="0"/>
      <xs:element name="FileDependency" type="xs:string" minOccurs="0"/>
      <xs:element name="JobCompletionCodeRules" type="xs:string" minOccurs="0"/>
      <xs:element name="LogicalResourceDependencies" type="xs:string" minOccurs="0"/>
      <xs:element name="Documentation" type="NullableString" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Stream Contact Persons -->
  <xs:complexType name="StreamContactPersonsType">
    <xs:sequence>
      <xs:element name="StreamContactPerson" type="StreamContactPersonType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Stream Contact Person -->
  <xs:complexType name="StreamContactPersonType">
    <xs:sequence>
      <xs:element name="FirstName" type="xs:string"/>
      <xs:element name="LastName" type="xs:string"/>
      <xs:element name="MiddleName" type="xs:string" minOccurs="0"/>
      <xs:element name="CompanyName" type="xs:string"/>
      <xs:element name="Department" type="xs:string" minOccurs="0"/>
      <xs:element name="Comment" type="NullableString"/>
      <xs:element name="ContactType" type="xs:string"/>
      <xs:element name="HierarchyLevelCd" type="xs:int"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Schedule Rule -->
  <xs:complexType name="ScheduleRuleType">
    <xs:sequence>
      <xs:element name="ScheduleRuleXml">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>

  <!-- Stream Version Detail -->
  <xs:complexType name="StreamVersionDetailType">
    <xs:sequence>
      <xs:element name="StreamVersionType" type="xs:string"/>
      <xs:element name="StreamVersion" type="xs:string"/>
      <xs:element name="DeploymentDateTime" type="xs:string"/>
      <xs:element name="DeployAsActive" type="xs:boolean"/>
      <xs:element name="PlannedDeploymentDateTime" type="xs:string" minOccurs="0"/>
      <xs:element name="StorageDateTime" type="xs:string" minOccurs="0"/>
      <xs:element name="AutoDeploymentStatus" type="xs:string"/>
      <xs:element name="ScheduleRulesMergeType" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Preparation Script -->
  <xs:complexType name="PreparationScriptType">
    <xs:sequence>
      <xs:element name="Script">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="ScriptLanguage" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Job Preparation Script -->
  <xs:complexType name="JobPreparationScriptType">
    <xs:sequence>
      <xs:element name="PreparationScriptJobOrder" type="xs:int"/>
      <xs:element name="Script">
        <xs:complexType mixed="true">
          <xs:simpleContent>
            <xs:extension base="xs:string"/>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="ScriptLanguage" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>

  <!-- Nullable Types -->
  <xs:complexType name="NullableString">
    <xs:simpleContent>
      <xs:extension base="xs:string">
        <xs:attribute name="IsNull" type="xs:boolean" use="optional"/>
      </xs:extension>
    </xs:simpleContent>
  </xs:complexType>

  <xs:complexType name="NullableInt">
    <xs:simpleContent>
      <xs:extension base="xs:string">
        <xs:attribute name="IsNull" type="xs:boolean" use="optional"/>
      </xs:extension>
    </xs:simpleContent>
  </xs:complexType>

  <xs:complexType name="NullableBoolean">
    <xs:simpleContent>
      <xs:extension base="xs:string">
        <xs:attribute name="IsNull" type="xs:boolean" use="optional"/>
      </xs:extension>
    </xs:simpleContent>
  </xs:complexType>

  <!-- Enumerations -->
  <xs:simpleType name="StreamTypeEnum">
    <xs:restriction base="xs:string">
      <xs:enumeration value="Normal"/>
      <xs:enumeration value="Real"/>
      <xs:enumeration value="Master"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="JobTypeEnum">
    <xs:restriction base="xs:string">
      <xs:enumeration value="None"/>
      <xs:enumeration value="Windows"/>
      <xs:enumeration value="Unix"/>
      <xs:enumeration value="Zos"/>
      <xs:enumeration value="BS2000"/>
      <xs:enumeration value="AS400"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="JobCategoryEnum">
    <xs:restriction base="xs:string">
      <xs:enumeration value="StartPoint"/>
      <xs:enumeration value="EndPoint"/>
      <xs:enumeration value="Endpoint"/>
      <xs:enumeration value="Job"/>
      <xs:enumeration value="Normal"/>
      <xs:enumeration value="RecoveryJobNetStartPoint"/>
      <xs:enumeration value="RecoveryJobNetEndPoint"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="TemplateTypeEnum">
    <xs:restriction base="xs:string">
      <xs:enumeration value="Normal"/>
      <xs:enumeration value="FileTransfer"/>
    </xs:restriction>
  </xs:simpleType>

</xs:schema>'''

        return xsd_content

    def save_xsd_schema(self, output_file: str):
        """Save generated XSD schema to file"""
        xsd_content = self.generate_base_xsd()

        # Pretty format the XSD
        try:
            dom = parseString(xsd_content)
            pretty_xsd = dom.toprettyxml(indent="  ")
            # Remove empty lines
            lines = [line for line in pretty_xsd.split('\n') if line.strip()]
            formatted_xsd = '\n'.join(lines)
        except:
            # Fallback to original if formatting fails
            formatted_xsd = xsd_content

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_xsd)

        print(f"XSD Schema saved to: {output_file}")
        return formatted_xsd

def main():
    """Main function to generate XSD schema"""
    analysis_file = "/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/backend/analysis/xml_structure_analysis.json"
    output_file = "/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/backend/schemas/streamworks_export.xsd"

    # Create output directory
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Generate XSD
    generator = StreamworksXSDGenerator(analysis_file)
    xsd_content = generator.save_xsd_schema(output_file)

    print("\n" + "="*50)
    print("XSD SCHEMA GENERATION COMPLETE")
    print("="*50)
    print(f"Based on analysis of {generator.analysis['summary']['successfully_parsed']} real Streamworks exports")
    print(f"Schema includes {len(generator.element_freq)} unique elements")
    print(f"Supports {len(generator.analysis['summary']['stream_types'])} stream types")
    print(f"Supports {len(generator.analysis['summary']['job_types'])} job types")

if __name__ == "__main__":
    main()