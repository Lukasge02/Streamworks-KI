#!/usr/bin/env python3
"""
XML Structure Analyzer for Streamworks Export-Streams
Analyzes all available XML files to extract patterns and generate XSD schema
"""

import os
import xml.etree.ElementTree as ET
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
import re
from datetime import datetime

class StreamworksXMLAnalyzer:
    def __init__(self, export_streams_path: str):
        self.export_streams_path = Path(export_streams_path)
        self.structures = defaultdict(lambda: defaultdict(int))
        self.element_frequencies = Counter()
        self.attribute_patterns = defaultdict(set)
        self.text_content_patterns = defaultdict(list)
        self.stream_types = Counter()
        self.job_types = Counter()
        self.parsed_files = []
        self.failed_files = []

    def find_all_xml_files(self) -> List[Path]:
        """Find all XML files in Export-Streams directory"""
        xml_files = []

        # Look for .xml files
        xml_files.extend(self.export_streams_path.rglob("*.xml"))

        # Look for files with .xml_ok_* pattern
        for file in self.export_streams_path.rglob("*.xml_ok_*"):
            xml_files.append(file)

        return xml_files

    def extract_element_structure(self, element: ET.Element, path: str = "") -> Dict[str, Any]:
        """Recursively extract element structure"""
        current_path = f"{path}/{element.tag}" if path else element.tag

        # Count this element
        self.element_frequencies[current_path] += 1

        # Record attributes
        if element.attrib:
            for attr_name, attr_value in element.attrib.items():
                self.attribute_patterns[f"{current_path}@{attr_name}"].add(attr_value)

        # Record text content patterns
        if element.text and element.text.strip():
            self.text_content_patterns[current_path].append(element.text.strip())

        # Analyze children
        children = {}
        for child in element:
            child_structure = self.extract_element_structure(child, current_path)
            child_name = child.tag
            if child_name in children:
                # Handle multiple children with same name
                if not isinstance(children[child_name], list):
                    children[child_name] = [children[child_name]]
                children[child_name].append(child_structure)
            else:
                children[child_name] = child_structure

        return {
            "tag": element.tag,
            "attributes": dict(element.attrib),
            "text": element.text.strip() if element.text else None,
            "children": children
        }

    def analyze_stream_metadata(self, root: ET.Element) -> Dict[str, str]:
        """Extract metadata from stream"""
        metadata = {}

        # Find StreamName
        stream_name_elem = root.find(".//StreamName")
        if stream_name_elem is not None and stream_name_elem.text:
            metadata["stream_name"] = stream_name_elem.text

        # Find StreamType
        stream_type_elem = root.find(".//StreamType")
        if stream_type_elem is not None and stream_type_elem.text:
            metadata["stream_type"] = stream_type_elem.text
            self.stream_types[stream_type_elem.text] += 1

        # Find Job types
        job_elements = root.findall(".//Job")
        job_types_in_stream = []
        for job in job_elements:
            job_type_elem = job.find("JobType")
            template_type_elem = job.find("TemplateType")
            job_category_elem = job.find("JobCategory")

            if job_type_elem is not None and job_type_elem.text:
                job_types_in_stream.append(job_type_elem.text)
                self.job_types[job_type_elem.text] += 1

            if template_type_elem is not None and template_type_elem.text:
                job_types_in_stream.append(f"Template:{template_type_elem.text}")

            if job_category_elem is not None and job_category_elem.text:
                job_types_in_stream.append(f"Category:{job_category_elem.text}")

        metadata["job_types"] = job_types_in_stream
        return metadata

    def parse_xml_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single XML file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']
            content = None

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                raise Exception("Could not decode file with any encoding")

            # Parse XML
            root = ET.fromstring(content)

            # Extract structure
            structure = self.extract_element_structure(root)
            metadata = self.analyze_stream_metadata(root)

            return {
                "file_path": str(file_path),
                "structure": structure,
                "metadata": metadata,
                "file_size": file_path.stat().st_size
            }

        except Exception as e:
            self.failed_files.append({
                "file_path": str(file_path),
                "error": str(e)
            })
            return None

    def analyze_all_files(self) -> Dict[str, Any]:
        """Analyze all XML files"""
        xml_files = self.find_all_xml_files()
        print(f"Found {len(xml_files)} XML files to analyze...")

        for i, file_path in enumerate(xml_files):
            if i % 10 == 0:
                print(f"Processing file {i+1}/{len(xml_files)}: {file_path.name}")

            result = self.parse_xml_file(file_path)
            if result:
                self.parsed_files.append(result)

        print(f"\nAnalysis complete!")
        print(f"Successfully parsed: {len(self.parsed_files)} files")
        print(f"Failed to parse: {len(self.failed_files)} files")

        return self.generate_analysis_report()

    def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""

        # Find most common element patterns
        common_elements = self.element_frequencies.most_common(50)

        # Analyze attribute patterns
        attribute_analysis = {}
        for attr_path, values in self.attribute_patterns.items():
            attribute_analysis[attr_path] = {
                "unique_values": len(values),
                "common_values": list(values)[:10],  # Top 10 values
                "is_boolean": all(v.lower() in ['true', 'false'] for v in values),
                "is_null_pattern": any('isnull' in v.lower() for v in values)
            }

        # Analyze text content
        text_analysis = {}
        for element_path, texts in self.text_content_patterns.items():
            text_analysis[element_path] = {
                "sample_count": len(texts),
                "unique_values": len(set(texts)),
                "samples": texts[:5],  # First 5 samples
                "avg_length": sum(len(t) for t in texts) / len(texts) if texts else 0
            }

        # Generate structure hierarchy
        hierarchy = self._build_element_hierarchy()

        return {
            "summary": {
                "total_files_found": len(self.find_all_xml_files()),
                "successfully_parsed": len(self.parsed_files),
                "failed_to_parse": len(self.failed_files),
                "unique_elements": len(self.element_frequencies),
                "stream_types": dict(self.stream_types),
                "job_types": dict(self.job_types)
            },
            "element_frequency": dict(common_elements),
            "attribute_patterns": attribute_analysis,
            "text_content_patterns": text_analysis,
            "element_hierarchy": hierarchy,
            "failed_files": self.failed_files,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _build_element_hierarchy(self) -> Dict[str, Any]:
        """Build hierarchical view of XML elements"""
        hierarchy = {}

        for element_path in self.element_frequencies.keys():
            parts = element_path.split('/')
            current = hierarchy

            for part in parts:
                if part not in current:
                    current[part] = {
                        "frequency": self.element_frequencies[element_path],
                        "children": {}
                    }
                current = current[part]["children"]

        return hierarchy

    def save_analysis(self, output_file: str):
        """Save analysis results to JSON file"""
        analysis = self.generate_analysis_report()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"Analysis saved to: {output_file}")
        return analysis

def main():
    """Main analysis function"""
    export_streams_path = "/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/Export-Streams"
    output_file = "/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/backend/analysis/xml_structure_analysis.json"

    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Run analysis
    analyzer = StreamworksXMLAnalyzer(export_streams_path)
    analysis = analyzer.analyze_all_files()

    # Save results
    analyzer.save_analysis(output_file)

    # Print summary
    print("\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)
    print(f"Files analyzed: {analysis['summary']['successfully_parsed']}")
    print(f"Unique elements found: {analysis['summary']['unique_elements']}")
    print(f"Stream types: {analysis['summary']['stream_types']}")
    print(f"Job types: {list(analysis['summary']['job_types'].keys())}")
    print("\nMost common elements:")
    for element, count in list(analysis['element_frequency'].items())[:10]:
        print(f"  {element}: {count}")

if __name__ == "__main__":
    main()